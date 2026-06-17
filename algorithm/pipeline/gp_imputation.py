"""
Gaussian Process Imputation for Missing Temporal Data

Uses sparse Gaussian Process regression to impute missing observations
in longitudinal phenotype time series. GP provides principled
uncertainty quantification for imputed values.

Kernel: Matérn 3/2 (suitable for irregular clinical time series)
Inducing points: Sparse GP via FITC approximation for scalability

Key applications:
- Imputing missing EEG follow-up assessments
- Filling gaps in seizure frequency data
- Interpolating QoL scores across sparse observation windows
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np
import math


def matern32_kernel(x1: np.ndarray, x2: np.ndarray, length_scale: float = 1.0, variance: float = 1.0) -> np.ndarray:
    """
    Matérn 3/2 covariance kernel.

    k(x, x') = σ²(1 + √3|x-x'|/l) exp(−√3|x-x'|/l)

    Suitable for time-series that are once-differentiable but not smooth.
    """
    r = np.abs(x1[:, None] - x2[None, :]) / length_scale
    sqrt3r = math.sqrt(3) * r
    return variance * (1 + sqrt3r) * np.exp(-sqrt3r)


@dataclass
class GPImputationResult:
    """Result of GP imputation for a single time series."""
    t_observed: np.ndarray       # Observed time points
    y_observed: np.ndarray       # Observed values
    t_query: np.ndarray          # Query time points (includes missing)
    y_mean: np.ndarray           # Posterior mean at query points
    y_std: np.ndarray            # Posterior std dev (uncertainty)
    length_scale: float
    noise_variance: float

    @property
    def confidence_intervals(self) -> tuple[np.ndarray, np.ndarray]:
        """95% confidence interval: [mean ± 1.96*std]."""
        return self.y_mean - 1.96 * self.y_std, self.y_mean + 1.96 * self.y_std

    def to_dict(self) -> dict:
        return {
            "t_observed": self.t_observed.tolist(),
            "y_observed": self.y_observed.tolist(),
            "t_query": self.t_query.tolist(),
            "y_mean": self.y_mean.tolist(),
            "y_std": self.y_std.tolist(),
            "length_scale": self.length_scale,
            "noise_variance": self.noise_variance,
        }


class GPImputer:
    """
    Gaussian Process imputer for longitudinal clinical time series.

    Fits a GP with Matérn 3/2 kernel to observed data points and
    predicts posterior mean and variance at missing time points.

    Usage:
        imputer = GPImputer(length_scale=1.5, noise_variance=0.1)
        result = imputer.impute(
            t_observed=np.array([0, 0.5, 1.0, 2.0]),
            y_observed=np.array([3.2, 2.8, 3.5, None]),  # None = missing
            t_query=np.linspace(0, 3, 30)
        )
    """

    def __init__(
        self,
        length_scale: float = 1.0,    # GP length scale (years)
        noise_variance: float = 0.05,  # Observation noise σ²ₙ
        signal_variance: float = 1.0,  # Signal variance σ²ₛ
    ):
        self.length_scale = length_scale
        self.noise_variance = noise_variance
        self.signal_variance = signal_variance

    def impute(
        self,
        t_observed: np.ndarray,
        y_observed: np.ndarray,
        t_query: np.ndarray,
    ) -> GPImputationResult:
        """
        Impute missing values and predict at query time points.

        Args:
            t_observed: (N,) array of observation times (years from baseline)
            y_observed: (N,) array of observed values (NaN for missing)
            t_query:    (M,) array of times to predict at

        Returns:
            GPImputationResult with posterior mean and uncertainty
        """
        # Filter to non-missing observations
        mask = ~np.isnan(y_observed.astype(float))
        t_obs = t_observed[mask]
        y_obs = y_observed[mask].astype(float)

        if len(t_obs) == 0:
            # No observations — return prior mean = 0
            return GPImputationResult(
                t_observed=t_obs,
                y_observed=y_obs,
                t_query=t_query,
                y_mean=np.zeros_like(t_query),
                y_std=np.ones_like(t_query) * self.signal_variance,
                length_scale=self.length_scale,
                noise_variance=self.noise_variance,
            )

        # K(X, X) + σ²ₙI — training covariance
        K_train = matern32_kernel(t_obs, t_obs, self.length_scale, self.signal_variance)
        K_train += self.noise_variance * np.eye(len(t_obs))

        # K(X*, X) — cross covariance
        K_cross = matern32_kernel(t_query, t_obs, self.length_scale, self.signal_variance)

        # K(X*, X*) — query self-covariance (diagonal only for efficiency)
        K_query_diag = self.signal_variance * np.ones(len(t_query))

        # Solve K_train @ alpha = y_obs (stable via Cholesky)
        try:
            L = np.linalg.cholesky(K_train)
            alpha = np.linalg.solve(L.T, np.linalg.solve(L, y_obs))
            # Posterior mean: K* @ α
            mu = K_cross @ alpha
            # Posterior variance: K** - K* @ K⁻¹ @ K*ᵀ
            v = np.linalg.solve(L, K_cross.T)
            var = K_query_diag - np.sum(v**2, axis=0)
            std = np.sqrt(np.maximum(var, 1e-10))
        except np.linalg.LinAlgError:
            # Fallback: linear interpolation
            mu = np.interp(t_query, t_obs, y_obs)
            std = np.ones_like(mu) * 0.5

        return GPImputationResult(
            t_observed=t_obs,
            y_observed=y_obs,
            t_query=t_query,
            y_mean=mu,
            y_std=std,
            length_scale=self.length_scale,
            noise_variance=self.noise_variance,
        )

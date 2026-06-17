"""
Temporal Aggregation Utilities for Longitudinal Phenotype Data

Provides time-window aggregation, change detection, and trend
extraction over longitudinal clinical time series.

Core operations:
- Sliding window aggregation (mean, max, frequency)
- Change-point detection (CUSUM)
- Monotonic trend extraction (Mann-Kendall)
- Rolling feature extraction for ML pipelines
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, Sequence
import numpy as np


@dataclass
class WindowResult:
    center_time: float
    window_start: float
    window_end: float
    n_observations: int
    mean: float
    std: float
    minimum: float
    maximum: float


def sliding_window(
    times: np.ndarray,
    values: np.ndarray,
    window_width: float = 1.0,
    step: float = 0.5,
) -> list[WindowResult]:
    """
    Sliding window aggregation over an irregular time series.

    Args:
        times:        Observation times (years from baseline)
        values:       Observed values
        window_width: Width of each window (years)
        step:         Step size between window centers (years)

    Returns:
        List of WindowResult, one per window position
    """
    if len(times) == 0:
        return []

    t_start = times[0]
    t_end = times[-1]
    results = []

    center = t_start + window_width / 2
    while center - window_width / 2 <= t_end:
        wl = center - window_width / 2
        wr = center + window_width / 2
        mask = (times >= wl) & (times < wr)
        obs = values[mask]

        if len(obs) > 0:
            results.append(WindowResult(
                center_time=center,
                window_start=wl,
                window_end=wr,
                n_observations=int(len(obs)),
                mean=float(np.mean(obs)),
                std=float(np.std(obs)),
                minimum=float(np.min(obs)),
                maximum=float(np.max(obs)),
            ))
        center += step

    return results


def mann_kendall_trend(values: Sequence[float]) -> tuple[str, float]:
    """
    Mann-Kendall monotonic trend test.

    Returns:
        trend: "increasing", "decreasing", or "no_trend"
        tau:   Kendall's tau statistic ∈ [-1, 1]
    """
    n = len(values)
    v = list(values)
    s = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            s += (1 if v[j] > v[i] else (-1 if v[j] < v[i] else 0))

    total_pairs = n * (n - 1) / 2
    tau = s / total_pairs if total_pairs > 0 else 0.0

    if tau > 0.2:
        trend = "increasing"
    elif tau < -0.2:
        trend = "decreasing"
    else:
        trend = "no_trend"

    return trend, tau


def cusum_change_detection(
    values: np.ndarray,
    threshold: float = 3.0,
) -> list[int]:
    """
    CUSUM (Cumulative Sum) change-point detection.

    Args:
        values:    Time series array
        threshold: CUSUM decision threshold (in std deviations)

    Returns:
        List of indices where change points were detected
    """
    mean = np.mean(values)
    std = np.std(values) + 1e-8
    standardized = (values - mean) / std

    cusum_pos = np.zeros(len(values))
    cusum_neg = np.zeros(len(values))
    change_points = []

    for i in range(1, len(values)):
        cusum_pos[i] = max(0, cusum_pos[i-1] + standardized[i] - 0.5)
        cusum_neg[i] = max(0, cusum_neg[i-1] - standardized[i] - 0.5)

        if cusum_pos[i] > threshold or cusum_neg[i] > threshold:
            change_points.append(i)
            cusum_pos[i] = 0
            cusum_neg[i] = 0

    return change_points

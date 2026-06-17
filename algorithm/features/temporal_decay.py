"""
Temporal Decay Functions

δ(t, tₖ; γ) = e^(−γ(t − tₖ))

Implements exponential temporal decay weighting for evidence recency.
Older evidence contributes less to phenotype state resolution.
Decay rate γ is configurable per evidence domain.
"""

from __future__ import annotations
import math
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional


# Default decay rates γ (per year) for each evidence domain
DEFAULT_DECAY_RATES = {
    "seizure_event": 0.5,          # Moderate decay — older events still relevant
    "eeg_report": 1.0,             # Higher decay — EEG patterns can change
    "mri_report": 0.3,             # Low decay — structural findings are persistent
    "genetic_result": 0.0,         # No decay — genomic findings are permanent
    "medication_change": 2.0,      # High decay — med changes supersede quickly
    "clinical_note": 0.8,          # Moderate-high decay
    "neuropsychology_report": 0.4, # Moderate decay — cognitive phenotype changes slowly
    "autoimmune_panel": 1.5,       # High decay — immune status fluctuates
    "patient_reported": 1.2,       # High decay — PRO is time-sensitive
    "default": 0.7,                # Fallback
}


def temporal_decay(
    t_now: datetime,
    t_evidence: datetime,
    gamma: float = 0.7,
) -> float:
    """
    Compute exponential temporal decay weight.

    δ(t, tₖ; γ) = e^(−γ(t − tₖ))

    Args:
        t_now:       Current reference time t
        t_evidence:  Time of evidence recording tₖ
        gamma:       Decay rate γ (per year). Higher = faster decay.

    Returns:
        Decay weight ∈ (0, 1]. Weight is 1.0 when t == tₖ.
    """
    if t_evidence > t_now:
        # Future evidence gets no decay but should be scrutinized
        return 1.0

    delta_years = (t_now - t_evidence).total_seconds() / (365.25 * 24 * 3600)
    return math.exp(-gamma * delta_years)


def temporal_decay_batch(
    t_now: datetime,
    evidence_times: list[datetime],
    gamma: float = 0.7,
) -> list[float]:
    """Compute decay weights for a batch of evidence timestamps."""
    return [temporal_decay(t_now, t_k, gamma) for t_k in evidence_times]


def effective_weight(
    base_weight: float,
    t_now: datetime,
    t_evidence: datetime,
    gamma: float = 0.7,
) -> float:
    """
    Composite effective weight combining provenance tier and temporal decay.

    w_eff(cᵢ, t) = w(cᵢ) · δ(t, tᵢ; γ)

    Args:
        base_weight:  Provenance tier weight w(cᵢ)
        t_now:        Current reference time
        t_evidence:   Evidence timestamp
        gamma:        Decay rate

    Returns:
        Effective composite weight ∈ [0, 1]
    """
    return base_weight * temporal_decay(t_now, t_evidence, gamma)


@dataclass
class DecayConfig:
    """Configuration for domain-specific decay rates."""
    seizure_event: float = 0.5
    eeg_report: float = 1.0
    mri_report: float = 0.3
    genetic_result: float = 0.0
    medication_change: float = 2.0
    clinical_note: float = 0.8
    neuropsychology_report: float = 0.4
    autoimmune_panel: float = 1.5
    patient_reported: float = 1.2
    default: float = 0.7

    def get(self, domain: str) -> float:
        return getattr(self, domain, self.default)


def half_life_from_gamma(gamma: float) -> float:
    """Return the half-life in years for a given decay rate γ."""
    if gamma == 0:
        return float("inf")
    return math.log(2) / gamma


def gamma_from_half_life(half_life_years: float) -> float:
    """Return decay rate γ for a target half-life (in years)."""
    if half_life_years <= 0:
        raise ValueError("Half-life must be positive")
    return math.log(2) / half_life_years


class TemporalDecayEngine:
    """
    Engine for applying configurable temporal decay across evidence streams.

    Usage:
        engine = TemporalDecayEngine(config=DecayConfig())
        weight = engine.decay(t_now, t_evidence, domain="eeg_report")
        composite = engine.composite(base_w=0.6, t_now=..., t_k=..., domain="eeg_report")
    """

    def __init__(self, config: Optional[DecayConfig] = None):
        self.config = config or DecayConfig()

    def decay(self, t_now: datetime, t_evidence: datetime, domain: str = "default") -> float:
        gamma = self.config.get(domain)
        return temporal_decay(t_now, t_evidence, gamma)

    def composite(
        self,
        base_weight: float,
        t_now: datetime,
        t_evidence: datetime,
        domain: str = "default",
    ) -> float:
        gamma = self.config.get(domain)
        return effective_weight(base_weight, t_now, t_evidence, gamma)

    def summary(self) -> dict:
        """Return half-lives for all configured domains."""
        result = {}
        for domain in vars(self.config):
            gamma = self.config.get(domain)
            result[domain] = {
                "gamma": gamma,
                "half_life_years": half_life_from_gamma(gamma),
            }
        return result

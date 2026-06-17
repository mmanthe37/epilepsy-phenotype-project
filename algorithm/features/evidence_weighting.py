"""
Evidence Weighting & Provenance Tiering

Implements the heuristic confidence weighting system:
    w(cᵢ) = 1.0  for Tier 1 (specialist, lab-confirmed, clinical trial)
    w(cᵢ) = 0.6  for Tier 2 (structured EHR, primary care, pharmacy)
    w(cᵢ) = 0.2  for Tier 3 (patient-reported, caregiver, informal)
"""

from __future__ import annotations
from algorithm.core.evidence_ledger import LedgerEntry, SourceTier, TIER_WEIGHTS
from datetime import datetime
from typing import Sequence


def confidence_weight(source_tier: SourceTier) -> float:
    """Return base confidence weight for a provenance tier."""
    return TIER_WEIGHTS.get(source_tier, 0.2)


def aggregate_weighted_evidence(
    entries: Sequence[LedgerEntry],
    t_now: datetime,
    decay_engine=None,
    domain: str = "default",
) -> float:
    """
    Aggregate evidence across ledger entries using weighted combination.

    W_agg = Σᵢ [w(cᵢ) · δ(t, tᵢ; γ)] / n

    Returns normalized aggregate confidence score ∈ [0, 1].
    """
    if not entries:
        return 0.0

    total = 0.0
    for entry in entries:
        base_w = entry.confidence_weight
        if decay_engine is not None:
            w = decay_engine.composite(base_w, t_now, entry.timestamp, domain)
        else:
            w = base_w
        total += w

    return total / len(entries)


def tier_breakdown(entries: Sequence[LedgerEntry]) -> dict:
    """Return counts and mean weights by tier."""
    tiers = {1: [], 2: [], 3: []}
    for e in entries:
        tiers[e.tier_number].append(e.confidence_weight)

    return {
        tier: {
            "count": len(weights),
            "mean_weight": sum(weights) / len(weights) if weights else 0.0,
        }
        for tier, weights in tiers.items()
    }


def select_highest_confidence(entries: Sequence[LedgerEntry]) -> LedgerEntry | None:
    """Return the entry with the highest confidence weight."""
    if not entries:
        return None
    return max(entries, key=lambda e: e.confidence_weight)


def dominant_tier(entries: Sequence[LedgerEntry]) -> int | None:
    """Return the tier number that contributes most entries."""
    if not entries:
        return None
    counts = {1: 0, 2: 0, 3: 0}
    for e in entries:
        counts[e.tier_number] += 1
    return max(counts, key=counts.get)

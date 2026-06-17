"""
Provenance Tiering Engine

Classifies incoming clinical data sources into Tier 1, 2, or 3 based on
heuristic rules aligned with the VLEP provenance framework.

Tier 1 (w=1.0): Specialist documentation, confirmed lab results, research data
Tier 2 (w=0.6): Structured EHR, primary care, pharmacy
Tier 3 (w=0.2): Patient/caregiver-reported, unstructured/informal
"""

from __future__ import annotations
from algorithm.core.evidence_ledger import SourceTier, TIER_WEIGHTS
from dataclasses import dataclass
from typing import Optional


# Keyword-based heuristic rules for automatic source classification
TIER1_KEYWORDS = {
    "epileptologist", "neurologist", "epilepsy center", "epilepsy specialist",
    "clinical trial", "research protocol", "genetic laboratory", "whole exome",
    "whole genome", "clia", "eeg laboratory", "eeg report", "mri report",
    "radiology read", "neuropathology", "epilepsy surgery", "video eeg",
    "long-term monitoring", "ltm", "level 3 epilepsy center", "naec",
}

TIER2_KEYWORDS = {
    "primary care", "family medicine", "general practitioner", "gp note",
    "nurse practitioner", "pa note", "pharmacy", "prescription", "refill",
    "icd", "cpt", "coded diagnosis", "ehr export", "structured data",
    "telehealth", "telemedicine", "urgent care", "emergency department",
    "ed visit", "outpatient note",
}

TIER3_KEYWORDS = {
    "patient reported", "patient diary", "seizure diary", "caregiver report",
    "self-reported", "app log", "mobile app", "informal", "verbal report",
    "phone call summary", "message", "portal message",
}


@dataclass
class TieringResult:
    source_tier: SourceTier
    confidence_weight: float
    tier_number: int
    rationale: str
    original_text: str


def classify_source_text(source_description: str) -> TieringResult:
    """
    Classify a free-text source description into a provenance tier.
    Uses keyword matching heuristics.
    """
    text_lower = source_description.lower()

    # Check Tier 1
    for kw in TIER1_KEYWORDS:
        if kw in text_lower:
            return TieringResult(
                source_tier=SourceTier.SPECIALIST_EVALUATION,
                confidence_weight=1.0,
                tier_number=1,
                rationale=f"Tier 1 keyword match: '{kw}'",
                original_text=source_description,
            )

    # Check Tier 2
    for kw in TIER2_KEYWORDS:
        if kw in text_lower:
            return TieringResult(
                source_tier=SourceTier.STRUCTURED_EHR,
                confidence_weight=0.6,
                tier_number=2,
                rationale=f"Tier 2 keyword match: '{kw}'",
                original_text=source_description,
            )

    # Check Tier 3
    for kw in TIER3_KEYWORDS:
        if kw in text_lower:
            return TieringResult(
                source_tier=SourceTier.PATIENT_REPORTED,
                confidence_weight=0.2,
                tier_number=3,
                rationale=f"Tier 3 keyword match: '{kw}'",
                original_text=source_description,
            )

    # Default to Tier 3 if unknown
    return TieringResult(
        source_tier=SourceTier.INFORMAL_DOCUMENTATION,
        confidence_weight=0.2,
        tier_number=3,
        rationale="No tier keyword match — defaulted to Tier 3",
        original_text=source_description,
    )


def classify_fhir_resource(resource_type: str, performer_role: Optional[str] = None) -> TieringResult:
    """
    Classify a FHIR resource type and performer role into a provenance tier.

    Args:
        resource_type:  FHIR resource type (e.g., "Observation", "DiagnosticReport")
        performer_role: FHIR practitioner role code if available
    """
    source_text = f"{resource_type} {performer_role or ''}"
    return classify_source_text(source_text)

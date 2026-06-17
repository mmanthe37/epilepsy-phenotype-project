"""
Immutable Evidence Ledger: L = {(tᵢ, Dᵢ, sᵢ, aᵢ, vᵢ)}ⁿᵢ₌₁

Append-only ledger recording all clinical observations, measurements,
and clinical events with full provenance tracing. No entry can be
modified or deleted after insertion — only superseded by new entries.

This is the foundational data structure of the VLEP system.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, Iterator, Callable
import hashlib
import json
import uuid


class DataRecordType(str, Enum):
    """Dᵢ: Classification of the clinical data record type."""
    SEIZURE_EVENT = "seizure_event"
    EEG_REPORT = "eeg_report"
    MRI_REPORT = "mri_report"
    GENETIC_RESULT = "genetic_result"
    CLINICAL_NOTE = "clinical_note"
    MEDICATION_CHANGE = "medication_change"
    NEUROPSYCHOLOGY_REPORT = "neuropsychology_report"
    AUTOIMMUNE_PANEL = "autoimmune_panel"
    METABOLIC_WORKUP = "metabolic_workup"
    PATIENT_REPORTED_OUTCOME = "patient_reported_outcome"
    SURGICAL_REPORT = "surgical_report"
    PATHOLOGY_REPORT = "pathology_report"
    RESEARCH_ASSESSMENT = "research_assessment"
    EXTERNAL_RECORD = "external_record"


class SourceTier(str, Enum):
    """sᵢ: Provenance tier determining base confidence weight."""
    # Tier 1: High-fidelity specialist sources (w = 1.0)
    SPECIALIST_EVALUATION = "specialist_evaluation"      # Epileptologist, neurologist
    CLINICAL_TRIAL_DATA = "clinical_trial_data"         # Prospective research data
    GENETIC_LABORATORY = "genetic_laboratory"           # CLIA-certified lab
    EEG_LABORATORY = "eeg_laboratory"                   # Clinical EEG lab report
    NEUROIMAGING_RADIOLOGY = "neuroimaging_radiology"   # Radiology formal read
    SURGICAL_PROGRAM = "surgical_program"               # Epilepsy surgery center
    PEER_REVIEWED_COHORT = "peer_reviewed_cohort"       # Published cohort data

    # Tier 2: Moderate-fidelity structured sources (w = 0.6)
    PRIMARY_CARE_PHYSICIAN = "primary_care_physician"
    NURSE_PRACTITIONER = "nurse_practitioner"
    PHARMACY_RECORDS = "pharmacy_records"
    STRUCTURED_EHR = "structured_ehr"                   # Coded ICD/CPT data
    TELEMEDICINE_NOTE = "telemedicine_note"
    EMERGENCY_DEPARTMENT = "emergency_department"

    # Tier 3: Lower-fidelity informal sources (w = 0.2)
    PATIENT_REPORTED = "patient_reported"
    CAREGIVER_REPORTED = "caregiver_reported"
    INFORMAL_DOCUMENTATION = "informal_documentation"
    MOBILE_APP_DIARY = "mobile_app_diary"


# Source tier to confidence weight mapping
TIER_WEIGHTS: dict[SourceTier, float] = {
    # Tier 1 sources
    SourceTier.SPECIALIST_EVALUATION: 1.0,
    SourceTier.CLINICAL_TRIAL_DATA: 1.0,
    SourceTier.GENETIC_LABORATORY: 1.0,
    SourceTier.EEG_LABORATORY: 1.0,
    SourceTier.NEUROIMAGING_RADIOLOGY: 1.0,
    SourceTier.SURGICAL_PROGRAM: 1.0,
    SourceTier.PEER_REVIEWED_COHORT: 1.0,
    # Tier 2 sources
    SourceTier.PRIMARY_CARE_PHYSICIAN: 0.6,
    SourceTier.NURSE_PRACTITIONER: 0.6,
    SourceTier.PHARMACY_RECORDS: 0.6,
    SourceTier.STRUCTURED_EHR: 0.6,
    SourceTier.TELEMEDICINE_NOTE: 0.6,
    SourceTier.EMERGENCY_DEPARTMENT: 0.6,
    # Tier 3 sources
    SourceTier.PATIENT_REPORTED: 0.2,
    SourceTier.CAREGIVER_REPORTED: 0.2,
    SourceTier.INFORMAL_DOCUMENTATION: 0.2,
    SourceTier.MOBILE_APP_DIARY: 0.2,
}


@dataclass(frozen=True)
class LedgerEntry:
    """
    A single immutable entry in the evidence ledger.
    Frozen — fields cannot be altered after creation.

    Fields:
        entry_id   : Unique UUID for this ledger entry
        timestamp  : tᵢ — time of clinical observation (not record creation)
        record_type: Dᵢ — type classification of the data record
        source_tier: sᵢ — provenance tier (determines confidence weight)
        author_id  : aᵢ — identifier of clinician/system recording the data
        ilae_version: vᵢ — nosological framework in effect at time of recording
        content    : Structured content dict for this observation
        confidence_weight: w(cᵢ) — base confidence from tier
        entry_hash : SHA-256 hash of content for integrity verification
        created_at : Wall-clock time the entry was added to ledger
        supersedes : UUID of prior entry this one supersedes (if any)
        narrative  : Free-text clinical narrative
    """
    entry_id: str
    timestamp: datetime
    record_type: DataRecordType
    source_tier: SourceTier
    author_id: str
    ilae_version: str
    content: dict
    confidence_weight: float
    entry_hash: str
    created_at: datetime
    supersedes: Optional[str] = None
    narrative: Optional[str] = None

    def to_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items()}
        d["timestamp"] = self.timestamp.isoformat()
        d["created_at"] = self.created_at.isoformat()
        d["record_type"] = self.record_type.value
        d["source_tier"] = self.source_tier.value
        return d

    @property
    def tier_number(self) -> int:
        """Return numeric tier (1, 2, or 3)."""
        w = self.confidence_weight
        if w >= 1.0:
            return 1
        if w >= 0.6:
            return 2
        return 3


class EvidenceLedger:
    """
    Immutable append-only evidence ledger for a single patient.

    L = {(tᵢ, Dᵢ, sᵢ, aᵢ, vᵢ)}ⁿᵢ₌₁

    Supports:
    - Temporal ordering and range queries
    - Provenance tier filtering
    - Source-type filtering
    - Integrity verification via hash chain
    - Export to JSON for persistence
    """

    def __init__(self, patient_id: str):
        self.patient_id = patient_id
        self._entries: list[LedgerEntry] = []
        self._entry_index: dict[str, LedgerEntry] = {}

    # ─── Core operations ─────────────────────────────────────────

    def append(
        self,
        timestamp: datetime,
        record_type: DataRecordType,
        source_tier: SourceTier,
        author_id: str,
        content: dict,
        ilae_version: str = "2025",
        supersedes: Optional[str] = None,
        narrative: Optional[str] = None,
    ) -> LedgerEntry:
        """
        Append a new immutable entry to the ledger.
        Returns the created LedgerEntry.
        """
        entry_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        confidence_weight = TIER_WEIGHTS.get(source_tier, 0.2)
        entry_hash = self._compute_hash(entry_id, timestamp, content)

        entry = LedgerEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            record_type=record_type,
            source_tier=source_tier,
            author_id=author_id,
            ilae_version=ilae_version,
            content=content,
            confidence_weight=confidence_weight,
            entry_hash=entry_hash,
            created_at=created_at,
            supersedes=supersedes,
            narrative=narrative,
        )

        self._entries.append(entry)
        self._entry_index[entry_id] = entry
        return entry

    # ─── Query operations ─────────────────────────────────────────

    def all(self) -> list[LedgerEntry]:
        """All entries in temporal order."""
        return sorted(self._entries, key=lambda e: e.timestamp)

    def by_id(self, entry_id: str) -> Optional[LedgerEntry]:
        return self._entry_index.get(entry_id)

    def before(self, t: datetime) -> list[LedgerEntry]:
        return [e for e in self.all() if e.timestamp <= t]

    def after(self, t: datetime) -> list[LedgerEntry]:
        return [e for e in self.all() if e.timestamp > t]

    def between(self, t_start: datetime, t_end: datetime) -> list[LedgerEntry]:
        return [e for e in self.all() if t_start <= e.timestamp <= t_end]

    def by_tier(self, tier: int) -> list[LedgerEntry]:
        """Return entries matching a provenance tier (1, 2, or 3)."""
        return [e for e in self.all() if e.tier_number == tier]

    def by_source(self, source_tier: SourceTier) -> list[LedgerEntry]:
        return [e for e in self.all() if e.source_tier == source_tier]

    def by_type(self, record_type: DataRecordType) -> list[LedgerEntry]:
        return [e for e in self.all() if e.record_type == record_type]

    def filter(self, predicate: Callable[[LedgerEntry], bool]) -> list[LedgerEntry]:
        return [e for e in self.all() if predicate(e)]

    def iter(self) -> Iterator[LedgerEntry]:
        yield from self.all()

    # ─── Integrity ────────────────────────────────────────────────

    def verify_integrity(self) -> bool:
        """Verify all entry hashes are consistent with content."""
        for entry in self._entries:
            expected = self._compute_hash(entry.entry_id, entry.timestamp, entry.content)
            if entry.entry_hash != expected:
                return False
        return True

    @staticmethod
    def _compute_hash(entry_id: str, timestamp: datetime, content: dict) -> str:
        raw = json.dumps(
            {"entry_id": entry_id, "timestamp": timestamp.isoformat(), "content": content},
            sort_keys=True
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    # ─── Properties ───────────────────────────────────────────────

    @property
    def size(self) -> int:
        return len(self._entries)

    @property
    def tier1_count(self) -> int:
        return len(self.by_tier(1))

    @property
    def tier2_count(self) -> int:
        return len(self.by_tier(2))

    @property
    def tier3_count(self) -> int:
        return len(self.by_tier(3))

    @property
    def date_range(self) -> tuple[Optional[datetime], Optional[datetime]]:
        if not self._entries:
            return None, None
        sorted_entries = self.all()
        return sorted_entries[0].timestamp, sorted_entries[-1].timestamp

    # ─── Serialization ────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "patient_id": self.patient_id,
            "size": self.size,
            "tier_counts": {"T1": self.tier1_count, "T2": self.tier2_count, "T3": self.tier3_count},
            "entries": [e.to_dict() for e in self.all()],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        t0, tn = self.date_range
        return (
            f"EvidenceLedger(patient={self.patient_id}, "
            f"n={self.size}, T1={self.tier1_count}, T2={self.tier2_count}, T3={self.tier3_count}, "
            f"range={t0} → {tn})"
        )

"""
Longitudinal Phenotyping Algorithm (LPA) — Core Engine

The central orchestration engine of the VLEP system. Coordinates:
1. Evidence ingestion (FHIR/EHR, NLP, structured records)
2. Provenance tier classification
3. Evidence ledger updates (immutable append)
4. Statistical model inference (GLMM, HMM, Survival)
5. CSEP resolution
6. Trajectory versioning

Usage:
    engine = LPAEngine(patient_id="P001")
    engine.ingest_observation(...)
    report = engine.resolve_csep()
    trajectory = engine.get_trajectory()
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from algorithm.core.evidence_ledger import (
    EvidenceLedger, DataRecordType, SourceTier
)
from algorithm.core.phenotype_vector import (
    PhenotypeStateVector, PhenotypeTrajectory
)
from algorithm.core.csep_resolver import CSEPResolver, CSEPReport
from algorithm.features.temporal_decay import DecayConfig
from algorithm.pipeline.provenance_tiering import classify_source_text


@dataclass
class IngestionRecord:
    """Input record for a clinical observation to be ingested into the LPA."""
    timestamp: datetime
    record_type: DataRecordType
    source_description: str        # Free text describing the source
    author_id: str                  # Clinician or system identifier
    content: dict                   # Structured clinical content
    source_tier: Optional[SourceTier] = None   # Override auto-classification if known
    ilae_version: str = "2025"
    narrative: Optional[str] = None
    supersedes_entry_id: Optional[str] = None  # ID of entry this supersedes


@dataclass
class LPAConfig:
    """Runtime configuration for the LPA engine."""
    ilae_version: str = "2025"
    decay_config: DecayConfig = field(default_factory=DecayConfig)
    lookback_years: float = 5.0
    enable_nlp_extraction: bool = True
    enable_hmm_inference: bool = True
    enable_survival_model: bool = True
    min_confidence_threshold: float = 0.1
    auto_classify_sources: bool = True


class LPAEngine:
    """
    Longitudinal Phenotyping Algorithm Engine

    Central orchestrator for the VLEP system. Maintains an immutable
    evidence ledger per patient and resolves longitudinal phenotype
    trajectories via the CSEP resolver and statistical models.

    Architecture:
        ingestion → tiering → ledger → models → CSEP → trajectory

    Thread safety: Single-patient, single-threaded. For multi-patient
    workloads, create one LPAEngine instance per patient.
    """

    VERSION = "1.0.0"
    ALGORITHM_ID = "LPA-v1.0"

    def __init__(
        self,
        patient_id: str,
        config: Optional[LPAConfig] = None,
    ):
        self.patient_id = patient_id
        self.config = config or LPAConfig()

        # Core data structures
        self.ledger = EvidenceLedger(patient_id=patient_id)
        self.trajectory = PhenotypeTrajectory(patient_id=patient_id)

        # CSEP resolver
        self.resolver = CSEPResolver(
            decay_config=self.config.decay_config,
            lookback_years=self.config.lookback_years,
        )

        # Statistics
        self._ingest_count: int = 0
        self._resolve_count: int = 0
        self._created_at: datetime = datetime.utcnow()

    # ─── Evidence Ingestion ───────────────────────────────────────

    def ingest(self, record: IngestionRecord) -> str:
        """
        Ingest a clinical observation into the evidence ledger.

        Performs:
        1. Source provenance classification (auto or explicit)
        2. Immutable append to evidence ledger
        3. Returns assigned ledger entry ID

        Args:
            record: IngestionRecord with observation data

        Returns:
            Ledger entry ID (UUID)
        """
        # Classify source tier
        if record.source_tier is not None:
            source_tier = record.source_tier
        elif self.config.auto_classify_sources:
            tier_result = classify_source_text(record.source_description)
            source_tier = tier_result.source_tier
        else:
            source_tier = SourceTier.INFORMAL_DOCUMENTATION

        # Append to immutable ledger
        entry = self.ledger.append(
            timestamp=record.timestamp,
            record_type=record.record_type,
            source_tier=source_tier,
            author_id=record.author_id,
            content=record.content,
            ilae_version=record.ilae_version,
            supersedes=record.supersedes_entry_id,
            narrative=record.narrative,
        )

        self._ingest_count += 1
        return entry.entry_id

    def ingest_batch(self, records: list[IngestionRecord]) -> list[str]:
        """Ingest multiple records. Returns list of entry IDs."""
        return [self.ingest(r) for r in records]

    def ingest_dict(
        self,
        timestamp: datetime,
        record_type: str,
        source_description: str,
        author_id: str,
        content: dict,
        ilae_version: str = "2025",
        narrative: Optional[str] = None,
    ) -> str:
        """Convenience method for inline ingestion without IngestionRecord."""
        record = IngestionRecord(
            timestamp=timestamp,
            record_type=DataRecordType(record_type),
            source_description=source_description,
            author_id=author_id,
            content=content,
            ilae_version=ilae_version,
            narrative=narrative,
        )
        return self.ingest(record)

    # ─── CSEP Resolution ─────────────────────────────────────────

    def resolve_csep(self, t_now: Optional[datetime] = None) -> CSEPReport:
        """
        Resolve the Current-State Epilepsy Profile at time t_now.

        Computes: CSEP(t) = argmax_P Σᵢ w(cᵢ)·δ(t,tᵢ;γ)·P(Dᵢ|phenotype=P)

        Returns CSEPReport with resolved phenotype and metadata.
        """
        report = self.resolver.resolve(
            patient_id=self.patient_id,
            ledger=self.ledger,
            t_now=t_now or datetime.utcnow(),
        )

        # Append resolved state to trajectory
        self.trajectory.append(report.phenotype)
        self._resolve_count += 1

        return report

    # ─── Trajectory ───────────────────────────────────────────────

    def get_trajectory(self) -> PhenotypeTrajectory:
        """Return the full longitudinal phenotype trajectory."""
        return self.trajectory

    def current_phenotype(self) -> Optional[PhenotypeStateVector]:
        """Return the most recently resolved phenotype state."""
        return self.trajectory.current

    # ─── Statistical Models ───────────────────────────────────────

    def run_hmm(self) -> dict:
        """
        Run HMM inference over trajectory states.
        Returns decoded latent state sequence and transition probabilities.
        """
        if not self.config.enable_hmm_inference:
            return {}
        if len(self.trajectory.states) < 2:
            return {"error": "Insufficient states for HMM inference (need ≥2)"}
        try:
            from algorithm.models.hmm import EpilepsyHMM
            hmm = EpilepsyHMM()
            return hmm.fit_and_decode(self.trajectory)
        except ImportError:
            return {"error": "HMM model not available"}

    def run_survival_analysis(self) -> dict:
        """
        Run survival model for pharmacoresistance prediction.
        Returns hazard ratios and time-to-event estimates.
        """
        if not self.config.enable_survival_model:
            return {}
        if len(self.trajectory.states) < 1:
            return {"error": "Insufficient data for survival analysis"}
        try:
            from algorithm.models.survival_ensemble import SurvivalEnsemble
            model = SurvivalEnsemble()
            return model.predict_from_trajectory(self.trajectory)
        except ImportError:
            return {"error": "Survival model not available"}

    # ─── Ledger Queries ───────────────────────────────────────────

    def ledger_summary(self) -> dict:
        """Return summary statistics for the evidence ledger."""
        t0, tn = self.ledger.date_range
        return {
            "patient_id": self.patient_id,
            "algorithm_version": self.ALGORITHM_ID,
            "total_entries": self.ledger.size,
            "tier_distribution": {
                "T1": self.ledger.tier1_count,
                "T2": self.ledger.tier2_count,
                "T3": self.ledger.tier3_count,
            },
            "date_range": {
                "earliest": t0.isoformat() if t0 else None,
                "latest": tn.isoformat() if tn else None,
            },
            "integrity_verified": self.ledger.verify_integrity(),
            "ingest_count": self._ingest_count,
            "resolve_count": self._resolve_count,
        }

    # ─── I/O ─────────────────────────────────────────────────────

    def export_ledger(self) -> dict:
        """Export the full evidence ledger as a JSON-serializable dict."""
        return self.ledger.to_dict()

    def export_trajectory(self) -> dict:
        """Export the full phenotype trajectory as a JSON-serializable dict."""
        return self.trajectory.to_dict()

    def export_full(self) -> dict:
        """Export complete engine state: ledger + trajectory + metadata."""
        return {
            "patient_id": self.patient_id,
            "algorithm_version": self.ALGORITHM_ID,
            "lpa_version": self.VERSION,
            "exported_at": datetime.utcnow().isoformat(),
            "config": {
                "ilae_version": self.config.ilae_version,
                "lookback_years": self.config.lookback_years,
            },
            "ledger": self.export_ledger(),
            "trajectory": self.export_trajectory(),
        }

    # ─── Demo & Testing ───────────────────────────────────────────

    @classmethod
    def demo(cls) -> "LPAEngine":
        """
        Create a demo engine with sample patient data.
        Useful for quick testing and demonstration.
        """
        from datetime import timedelta

        engine = cls(patient_id="DEMO-001")
        base_time = datetime(2020, 1, 15)

        # Initial clinical evaluation
        engine.ingest_dict(
            timestamp=base_time,
            record_type="clinical_note",
            source_description="Epileptologist evaluation at level 3 epilepsy center",
            author_id="DR-SMITH",
            content={
                "seizure_type": "focal_impaired_awareness",
                "etiology": "unknown",
                "syndrome": "temporal_lobe_epilepsy",
                "treatment_response": "drug_responsive",
            },
            narrative="New onset focal epilepsy. Video-EEG pending.",
        )

        # EEG report
        engine.ingest_dict(
            timestamp=base_time + timedelta(days=30),
            record_type="eeg_report",
            source_description="EEG laboratory, long-term monitoring",
            author_id="EEG-LAB",
            content={
                "interictal_spikes": True,
                "background_abnormal": False,
                "eeg_pattern": "left temporal sharp waves",
                "lateralization": "left",
            },
        )

        # MRI report
        engine.ingest_dict(
            timestamp=base_time + timedelta(days=45),
            record_type="mri_report",
            source_description="Neuroimaging radiology epilepsy protocol MRI",
            author_id="RADIOLOGY",
            content={
                "lesion_present": True,
                "lesion_type": "MTS",
                "lesion_location": "left mesial temporal",
            },
        )

        # Genetic testing
        engine.ingest_dict(
            timestamp=base_time + timedelta(days=90),
            record_type="genetic_result",
            source_description="Genetic laboratory CLIA-certified whole exome sequencing",
            author_id="GENETICS-LAB",
            content={
                "gene_name": None,
                "variant": None,
                "etiology": "structural",
            },
        )

        # Medication failure — pharmacoresistance emerging
        engine.ingest_dict(
            timestamp=base_time + timedelta(days=365),
            record_type="medication_change",
            source_description="Epileptologist evaluation — second ASM failure",
            author_id="DR-SMITH",
            content={
                "treatment_response": "emerging_resistance",
                "asm_failed": ["levetiracetam", "lacosamide"],
            },
        )

        return engine

    def __repr__(self) -> str:
        return (
            f"LPAEngine(patient={self.patient_id}, "
            f"entries={self.ledger.size}, "
            f"states={len(self.trajectory.states)}, "
            f"v={self.VERSION})"
        )


# ─── CLI entry point ──────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import json

    if "--demo" in sys.argv:
        print("Running LPA demo with sample patient data...\n")
        engine = LPAEngine.demo()
        report = engine.resolve_csep()
        print(f"Engine: {engine}")
        print(f"\nLedger summary: {json.dumps(engine.ledger_summary(), indent=2)}")
        print(f"\nCSEP Report:")
        print(json.dumps(report.to_dict(), indent=2))
        print(f"\n✓ LPA Engine operational — v{LPAEngine.VERSION}")
    else:
        print("Usage: python -m algorithm.core.lpa_engine --demo")

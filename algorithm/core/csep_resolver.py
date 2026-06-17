"""
CSEP Resolver — Current-State Epilepsy Profile

Synthesizes evidence from the immutable ledger into a structured,
clinician-interpretable Current-State Epilepsy Profile (CSEP).

Resolution function:
    CSEP(t) = argmax_P Σᵢ w(cᵢ) · δ(t, tᵢ; γ) · P(Dᵢ | phenotype = P)

The CSEP represents the most evidence-supported phenotype state at
time t, accounting for provenance quality and evidence recency.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from collections import defaultdict, Counter

from algorithm.core.evidence_ledger import (
    EvidenceLedger, LedgerEntry, DataRecordType, SourceTier
)
from algorithm.core.phenotype_vector import (
    PhenotypeStateVector, SeizureType, EtiologyClass,
    SyndromicClassification, TreatmentResponseState,
    BiomarkerVector, ComorbidityProfile
)
from algorithm.features.temporal_decay import TemporalDecayEngine, DecayConfig
from algorithm.features.evidence_weighting import aggregate_weighted_evidence


@dataclass
class CSEPReport:
    """
    Full Current-State Epilepsy Profile snapshot.
    Output of the CSEP resolver for a given patient at time t.
    """
    patient_id: str
    resolved_at: datetime
    phenotype: PhenotypeStateVector

    # Confidence metrics
    aggregate_confidence: float = 0.0
    evidence_count: int = 0
    tier1_count: int = 0
    tier2_count: int = 0
    tier3_count: int = 0

    # Key evidence supporting each dimension
    seizure_evidence: list[str] = field(default_factory=list)
    etiology_evidence: list[str] = field(default_factory=list)
    treatment_evidence: list[str] = field(default_factory=list)

    # Flags
    pharmacoresistant_flag: bool = False
    active_autoimmune_flag: bool = False
    unresolved_etiology_flag: bool = False
    high_comorbidity_burden: bool = False

    # Temporal span of evidence used
    earliest_evidence: Optional[datetime] = None
    latest_evidence: Optional[datetime] = None

    # Narrative summary
    clinical_summary: str = ""

    def to_dict(self) -> dict:
        return {
            "patient_id": self.patient_id,
            "resolved_at": self.resolved_at.isoformat(),
            "aggregate_confidence": round(self.aggregate_confidence, 4),
            "evidence_count": self.evidence_count,
            "tier_distribution": {
                "T1": self.tier1_count,
                "T2": self.tier2_count,
                "T3": self.tier3_count,
            },
            "phenotype": self.phenotype.to_dict(),
            "flags": {
                "pharmacoresistant": self.pharmacoresistant_flag,
                "active_autoimmune": self.active_autoimmune_flag,
                "unresolved_etiology": self.unresolved_etiology_flag,
                "high_comorbidity": self.high_comorbidity_burden,
            },
            "evidence_span": {
                "earliest": self.earliest_evidence.isoformat() if self.earliest_evidence else None,
                "latest": self.latest_evidence.isoformat() if self.latest_evidence else None,
            },
            "clinical_summary": self.clinical_summary,
        }


class CSEPResolver:
    """
    Resolves the Current-State Epilepsy Profile from an evidence ledger.

    Resolution strategy:
    1. Filter ledger entries to time window [−lookback, t_now]
    2. Apply temporal decay to each entry's base confidence weight
    3. For each phenotype dimension (S, E, C, B, M, R):
       - Score candidate values by weighted evidence sum
       - Select argmax as current-state value
    4. Compute aggregate confidence and flag clinical conditions
    5. Generate CSEP report
    """

    def __init__(
        self,
        decay_config: Optional[DecayConfig] = None,
        lookback_years: float = 5.0,
    ):
        self.decay_engine = TemporalDecayEngine(decay_config or DecayConfig())
        self.lookback_years = lookback_years

    def resolve(
        self,
        patient_id: str,
        ledger: EvidenceLedger,
        t_now: Optional[datetime] = None,
    ) -> CSEPReport:
        """
        Resolve CSEP for a patient from their evidence ledger at time t_now.

        Args:
            patient_id: Patient identifier
            ledger:     Patient's evidence ledger
            t_now:      Reference time (defaults to current UTC time)

        Returns:
            CSEPReport with resolved phenotype and confidence metadata
        """
        t_now = t_now or datetime.utcnow()

        # Get relevant entries within lookback window
        from datetime import timedelta
        t_start = datetime.fromtimestamp(
            max(0, t_now.timestamp() - self.lookback_years * 365.25 * 86400)
        )
        entries = ledger.between(t_start, t_now)

        if not entries:
            # No evidence available — return empty profile
            phenotype = PhenotypeStateVector.empty(t_now)
            return CSEPReport(
                patient_id=patient_id,
                resolved_at=t_now,
                phenotype=phenotype,
                clinical_summary="Insufficient evidence for phenotype resolution.",
            )

        # ─── Resolve each phenotype dimension ─────────────────────

        seizure_type = self._resolve_seizure_type(entries, t_now)
        etiology = self._resolve_etiology(entries, t_now)
        syndrome = self._resolve_syndrome(entries, t_now)
        treatment_response = self._resolve_treatment_response(entries, t_now)
        biomarkers = self._resolve_biomarkers(entries, t_now)
        comorbidities = self._resolve_comorbidities(entries, t_now)

        # ─── Compute aggregate confidence ─────────────────────────

        conf = aggregate_weighted_evidence(entries, t_now, self.decay_engine)
        tier_counts = {1: 0, 2: 0, 3: 0}
        for e in entries:
            tier_counts[e.tier_number] += 1

        # ─── Build phenotype vector ────────────────────────────────

        phenotype = PhenotypeStateVector(
            timestamp=t_now,
            seizure_type=seizure_type,
            etiology=etiology,
            syndrome=syndrome,
            biomarkers=biomarkers,
            comorbidities=comorbidities,
            treatment_response=treatment_response,
            confidence_score=conf,
            evidence_count=len(entries),
        )

        # ─── Detect clinical flags ─────────────────────────────────

        pharma_resistant = (treatment_response == TreatmentResponseState.PHARMACORESISTANT)
        unresolved_etiology = (etiology == EtiologyClass.UNKNOWN)
        high_comorbidity = (comorbidities.comorbidity_count >= 3)

        # ─── Build clinical summary ────────────────────────────────

        summary = self._generate_summary(phenotype, entries, pharma_resistant)

        date_range = ledger.date_range

        return CSEPReport(
            patient_id=patient_id,
            resolved_at=t_now,
            phenotype=phenotype,
            aggregate_confidence=conf,
            evidence_count=len(entries),
            tier1_count=tier_counts[1],
            tier2_count=tier_counts[2],
            tier3_count=tier_counts[3],
            pharmacoresistant_flag=pharma_resistant,
            unresolved_etiology_flag=unresolved_etiology,
            high_comorbidity_burden=high_comorbidity,
            earliest_evidence=date_range[0],
            latest_evidence=date_range[1],
            clinical_summary=summary,
        )

    # ─── Dimension resolvers ──────────────────────────────────────

    def _resolve_seizure_type(
        self, entries: list[LedgerEntry], t_now: datetime
    ) -> SeizureType:
        scores: dict[str, float] = defaultdict(float)
        relevant = [e for e in entries if e.record_type in {
            DataRecordType.SEIZURE_EVENT, DataRecordType.CLINICAL_NOTE,
            DataRecordType.EEG_REPORT
        }]
        for e in relevant:
            st = e.content.get("seizure_type")
            if st:
                w = self.decay_engine.composite(e.confidence_weight, t_now, e.timestamp, "seizure_event")
                scores[st] += w
        if not scores:
            return SeizureType.UNKNOWN_ONSET
        best = max(scores, key=scores.get)
        try:
            return SeizureType(best)
        except ValueError:
            return SeizureType.UNKNOWN_ONSET

    def _resolve_etiology(
        self, entries: list[LedgerEntry], t_now: datetime
    ) -> EtiologyClass:
        scores: dict[str, float] = defaultdict(float)
        relevant = [e for e in entries if e.record_type in {
            DataRecordType.GENETIC_RESULT, DataRecordType.MRI_REPORT,
            DataRecordType.CLINICAL_NOTE, DataRecordType.AUTOIMMUNE_PANEL,
            DataRecordType.METABOLIC_WORKUP
        }]
        for e in relevant:
            etio = e.content.get("etiology")
            if etio:
                w = self.decay_engine.composite(e.confidence_weight, t_now, e.timestamp, "genetic_result")
                scores[etio] += w
        if not scores:
            return EtiologyClass.UNKNOWN
        best = max(scores, key=scores.get)
        try:
            return EtiologyClass(best)
        except ValueError:
            return EtiologyClass.UNKNOWN

    def _resolve_syndrome(
        self, entries: list[LedgerEntry], t_now: datetime
    ) -> SyndromicClassification:
        scores: dict[str, float] = defaultdict(float)
        for e in entries:
            syndrome = e.content.get("syndrome")
            if syndrome:
                w = self.decay_engine.composite(e.confidence_weight, t_now, e.timestamp)
                scores[syndrome] += w
        if not scores:
            return SyndromicClassification.UNKNOWN_SYNDROME
        best = max(scores, key=scores.get)
        try:
            return SyndromicClassification(best)
        except ValueError:
            return SyndromicClassification.UNKNOWN_SYNDROME

    def _resolve_treatment_response(
        self, entries: list[LedgerEntry], t_now: datetime
    ) -> TreatmentResponseState:
        # Treatment response uses most recent high-confidence entry
        relevant = sorted(
            [e for e in entries if e.record_type == DataRecordType.MEDICATION_CHANGE
             and e.confidence_weight >= 0.6],
            key=lambda e: e.timestamp,
            reverse=True,
        )
        for e in relevant:
            tr = e.content.get("treatment_response")
            if tr:
                try:
                    return TreatmentResponseState(tr)
                except ValueError:
                    continue
        return TreatmentResponseState.UNKNOWN

    def _resolve_biomarkers(
        self, entries: list[LedgerEntry], t_now: datetime
    ) -> BiomarkerVector:
        bv = BiomarkerVector()
        eeg_entries = sorted(
            [e for e in entries if e.record_type == DataRecordType.EEG_REPORT],
            key=lambda e: e.timestamp, reverse=True
        )
        mri_entries = sorted(
            [e for e in entries if e.record_type == DataRecordType.MRI_REPORT],
            key=lambda e: e.timestamp, reverse=True
        )
        genetic_entries = [e for e in entries if e.record_type == DataRecordType.GENETIC_RESULT]

        if eeg_entries:
            latest_eeg = eeg_entries[0].content
            bv.eeg_interictal_spikes = latest_eeg.get("interictal_spikes")
            bv.eeg_background_abnormal = latest_eeg.get("background_abnormal")
            bv.eeg_pattern = latest_eeg.get("eeg_pattern")

        if mri_entries:
            latest_mri = mri_entries[0].content
            bv.mri_lesion_present = latest_mri.get("lesion_present")
            bv.mri_lesion_type = latest_mri.get("lesion_type")

        if genetic_entries:
            # Use highest-confidence genetic result
            best_genetic = max(genetic_entries, key=lambda e: e.confidence_weight)
            gc = best_genetic.content
            bv.gene_name = gc.get("gene_name")
            bv.pathogenic_variant = gc.get("variant")
            bv.variant_class = gc.get("variant_class")

        return bv

    def _resolve_comorbidities(
        self, entries: list[LedgerEntry], t_now: datetime
    ) -> ComorbidityProfile:
        cp = ComorbidityProfile()
        neuro_entries = [e for e in entries if e.record_type == DataRecordType.NEUROPSYCHOLOGY_REPORT]
        if neuro_entries:
            best = max(neuro_entries, key=lambda e: e.timestamp)
            c = best.content
            cp.depression_screen_positive = c.get("depression")
            cp.anxiety_screen_positive = c.get("anxiety")
            cp.intellectual_disability = c.get("intellectual_disability")
            cp.adhd = c.get("adhd")
            cp.quality_of_life_score = c.get("qol_score")
            cp.comorbidity_count = sum(1 for v in [
                cp.depression_screen_positive, cp.anxiety_screen_positive,
                cp.intellectual_disability, cp.adhd
            ] if v)
        return cp

    def _generate_summary(
        self,
        phenotype: PhenotypeStateVector,
        entries: list[LedgerEntry],
        pharma_resistant: bool,
    ) -> str:
        parts = [
            f"Seizure type: {phenotype.seizure_type.value.replace('_', ' ').title()}.",
            f"Etiology: {phenotype.etiology.value.replace('_', ' ').title()}.",
            f"Syndrome: {phenotype.syndrome.value.replace('_', ' ').title()}.",
            f"Treatment response: {phenotype.treatment_response.value.replace('_', ' ').title()}.",
        ]
        if pharma_resistant:
            parts.append("⚠ PHARMACORESISTANT — ≥2 adequate ASM trials failed.")
        parts.append(
            f"Evidence base: {len(entries)} observations "
            f"(confidence: {phenotype.confidence_score:.2%})."
        )
        return " ".join(parts)

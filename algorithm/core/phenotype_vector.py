"""
Phenotype Vector: P(t) = {S(t), E(t), C(t), B(t), M(t), R(t)}

Defines the six-dimensional longitudinal phenotype state vector for the
Versioned Longitudinal Epilepsy Phenotype (VLEP) system.

Each dimension captures a distinct clinical construct tracked across time.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional
import json


# ─────────────────────────────────────────────
#  Enumerations — ILAE 2017/2022/2025 aligned
# ─────────────────────────────────────────────

class SeizureType(str, Enum):
    """S(t): Seizure type cluster per ILAE 2017 operational classification."""
    FOCAL_AWARE = "focal_aware"
    FOCAL_IMPAIRED_AWARENESS = "focal_impaired_awareness"
    FOCAL_TO_BILATERAL_TONIC_CLONIC = "focal_to_bilateral_tonic_clonic"
    GENERALIZED_TONIC_CLONIC = "generalized_tonic_clonic"
    GENERALIZED_ABSENCE = "generalized_absence"
    GENERALIZED_MYOCLONIC = "generalized_myoclonic"
    GENERALIZED_ATONIC = "generalized_atonic"
    GENERALIZED_TONIC = "generalized_tonic"
    GENERALIZED_CLONIC = "generalized_clonic"
    SPASM = "spasm"
    UNKNOWN_ONSET = "unknown_onset"
    UNCLASSIFIED = "unclassified"


class EtiologyClass(str, Enum):
    """E(t): Etiology class per ILAE 2017 framework."""
    GENETIC = "genetic"
    STRUCTURAL = "structural"
    INFECTIOUS = "infectious"
    METABOLIC = "metabolic"
    IMMUNE = "immune"
    TRAUMATIC = "traumatic"
    POST_SURGICAL = "post_surgical"
    UNKNOWN = "unknown"
    COMBINED = "combined"


class SyndromicClassification(str, Enum):
    """C(t): Syndromic classification (ILAE-versioned, age-dependent)."""
    DRAVET_SYNDROME = "dravet_syndrome"
    LENNOX_GASTAUT_SYNDROME = "lennox_gastaut_syndrome"
    WEST_SYNDROME = "west_syndrome"
    CHILDHOOD_ABSENCE_EPILEPSY = "childhood_absence_epilepsy"
    JUVENILE_MYOCLONIC_EPILEPSY = "juvenile_myoclonic_epilepsy"
    JUVENILE_ABSENCE_EPILEPSY = "juvenile_absence_epilepsy"
    TEMPORAL_LOBE_EPILEPSY = "temporal_lobe_epilepsy"
    FRONTAL_LOBE_EPILEPSY = "frontal_lobe_epilepsy"
    ROLANDIC_EPILEPSY = "rolandic_epilepsy"
    PANAYIOTOPOULOS_SYNDROME = "panayiotopoulos_syndrome"
    KCNQ2_NEONATAL_EPILEPSY = "kcnq2_neonatal_epilepsy"
    SCN1A_RELATED = "scn1a_related"
    FEBRILE_SEIZURE_PLUS = "febrile_seizure_plus"
    PROGRESSIVE_MYOCLONIC_EPILEPSY = "progressive_myoclonic_epilepsy"
    UNKNOWN_SYNDROME = "unknown_syndrome"
    NOT_APPLICABLE = "not_applicable"


class TreatmentResponseState(str, Enum):
    """R(t): Treatment response trajectory."""
    DRUG_RESPONSIVE = "drug_responsive"
    PARTIAL_RESPONSE = "partial_response"
    EMERGING_RESISTANCE = "emerging_resistance"
    PHARMACORESISTANT = "pharmacoresistant"  # ≥2 adequate ASM trials failed
    SEIZURE_FREE = "seizure_free"
    SURGICAL_CANDIDATE = "surgical_candidate"
    POST_SURGICAL_SEIZURE_FREE = "post_surgical_seizure_free"
    POST_SURGICAL_NONRESPONDER = "post_surgical_nonresponder"
    UNKNOWN = "unknown"


# ─────────────────────────────────────────────
#  Sub-component dataclasses
# ─────────────────────────────────────────────

@dataclass
class BiomarkerVector:
    """
    B(t): Vector of validated biomarkers. Extends over time.
    Each field may be None when not yet assessed.
    """
    # EEG features
    eeg_interictal_spikes: Optional[bool] = None        # Interictal epileptiform discharges present
    eeg_background_abnormal: Optional[bool] = None      # Background slowing or disorganization
    eeg_hfos_present: Optional[bool] = None             # High-frequency oscillations (>80 Hz)
    eeg_pattern: Optional[str] = None                   # e.g. "3Hz spike-wave", "hypsarrhythmia"
    eeg_lateralization: Optional[str] = None            # "left", "right", "bilateral", "diffuse"

    # Neuroimaging
    mri_lesion_present: Optional[bool] = None
    mri_lesion_type: Optional[str] = None               # "FCD", "MTS", "tumor", "PMG", etc.
    mri_lesion_location: Optional[str] = None
    mri_volume_change: Optional[float] = None           # % volume change from baseline

    # Genetic / molecular
    pathogenic_variant: Optional[str] = None            # HGVS notation
    gene_name: Optional[str] = None                     # e.g. "SCN1A", "KCNQ2"
    variant_class: Optional[str] = None                 # "LOF", "GOF", "missense", "CNV"
    inheritance_pattern: Optional[str] = None           # "de novo", "autosomal dominant", etc.

    # CSF / blood
    csf_pleocytosis: Optional[bool] = None
    autoantibody_panel: Optional[dict] = None           # {antibody: titer}
    metabolic_marker: Optional[dict] = None             # {biomarker: value}


@dataclass
class ComorbidityProfile:
    """M(t): Comorbidity burden with domain-specific scores."""
    # Psychiatric
    depression_screen_positive: Optional[bool] = None
    anxiety_screen_positive: Optional[bool] = None
    psychosis_present: Optional[bool] = None
    suicidality_risk: Optional[str] = None              # "low", "moderate", "high"

    # Cognitive / developmental
    intellectual_disability: Optional[bool] = None
    id_severity: Optional[str] = None                   # "mild", "moderate", "severe", "profound"
    autism_spectrum_disorder: Optional[bool] = None
    adhd: Optional[bool] = None
    language_impairment: Optional[bool] = None

    # Behavioral
    behavioral_disorder_present: Optional[bool] = None
    sleep_disorder: Optional[bool] = None
    quality_of_life_score: Optional[float] = None       # QOLIE-31 or QOLIE-AD-48

    # Neurological
    stroke_history: Optional[bool] = None
    migraine: Optional[bool] = None
    cerebral_palsy: Optional[bool] = None

    # Systemic
    comorbidity_count: int = 0


# ─────────────────────────────────────────────
#  Phenotype State Vector
# ─────────────────────────────────────────────

@dataclass
class PhenotypeStateVector:
    """
    P(t) = {S(t), E(t), C(t), B(t), M(t), R(t)}

    Six-dimensional phenotypic state vector for a single temporal snapshot.
    All fields are typed, versioned, and audit-traceable.
    """
    timestamp: datetime

    # Core phenotype dimensions
    seizure_type: SeizureType = SeizureType.UNKNOWN_ONSET
    etiology: EtiologyClass = EtiologyClass.UNKNOWN
    syndrome: SyndromicClassification = SyndromicClassification.UNKNOWN_SYNDROME
    biomarkers: BiomarkerVector = field(default_factory=BiomarkerVector)
    comorbidities: ComorbidityProfile = field(default_factory=ComorbidityProfile)
    treatment_response: TreatmentResponseState = TreatmentResponseState.UNKNOWN

    # Confidence and provenance metadata
    confidence_score: float = 0.0           # Aggregate weighted confidence [0, 1]
    ilae_version: str = "2025"              # Nosological framework version
    resolved_by: str = "LPA-v1.0"          # Algorithm version that computed this state
    evidence_count: int = 0                 # Number of ledger entries used

    # Secondary seizure types (comorbid)
    secondary_seizure_types: list = field(default_factory=list)

    # Free-text annotation
    clinical_notes_summary: Optional[str] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)

    @classmethod
    def empty(cls, timestamp: Optional[datetime] = None) -> "PhenotypeStateVector":
        return cls(timestamp=timestamp or datetime.utcnow())

    def __repr__(self) -> str:
        return (
            f"PhenotypeStateVector("
            f"t={self.timestamp.date()}, "
            f"S={self.seizure_type.value}, "
            f"E={self.etiology.value}, "
            f"C={self.syndrome.value}, "
            f"R={self.treatment_response.value}, "
            f"conf={self.confidence_score:.3f})"
        )


@dataclass
class PhenotypeTrajectory:
    """
    T = {P(t₀), P(t₁), ..., P(tₙ)} — ordered phenotype state transitions.

    Captures the full longitudinal arc of a patient's epilepsy phenotype.
    """
    patient_id: str
    states: list[PhenotypeStateVector] = field(default_factory=list)

    def append(self, state: PhenotypeStateVector) -> None:
        self.states.append(state)
        self.states.sort(key=lambda s: s.timestamp)

    @property
    def current(self) -> Optional[PhenotypeStateVector]:
        return self.states[-1] if self.states else None

    @property
    def baseline(self) -> Optional[PhenotypeStateVector]:
        return self.states[0] if self.states else None

    def state_at(self, t: datetime) -> Optional[PhenotypeStateVector]:
        """Return the most recent state at or before time t."""
        prior = [s for s in self.states if s.timestamp <= t]
        return prior[-1] if prior else None

    def transitions(self) -> list[tuple]:
        """Return list of (from_state, to_state) transition pairs."""
        return [(self.states[i], self.states[i+1]) for i in range(len(self.states)-1)]

    def to_dict(self) -> dict:
        return {
            "patient_id": self.patient_id,
            "n_states": len(self.states),
            "states": [s.to_dict() for s in self.states]
        }

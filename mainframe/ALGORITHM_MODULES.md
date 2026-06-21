# VLEP Algorithm Modules Specification

**Project:** Epilepsy Phenotype Project  
**Component:** Versioned Longitudinal Epilepsy Phenotype (VLEP) Algorithm  
**File:** `mainframe/ALGORITHM_MODULES.md`  
**Version:** 0.1.0  
**Status:** Draft specification for v0.1 deterministic engine

This document defines the **modular decomposition** of the VLEP algorithm into independently versioned engines. Each module receives normalized ledger evidence and outputs typed phenotype assertions, risk scores, or meta-signals (confidence, conflicts, versioning triggers). Modules must be:

- **Pure functions over the evidence ledger** (plus configuration), producing deterministic outputs for a fixed `(L, N, algorithm_version)`.
- **Versioned** independently, with explicit input–output schemas.
- **Auditable**, with explicit links from outputs back to supporting `EvidenceLedgerEvent` IDs.

The global phenotype vector at time \(t\) is:

\[ P(t) = \{ S(t), E(t), C(t), B(t), M(t), R(t) \} \]

where:
- `S(t)`: seizure type cluster
- `E(t)`: etiology class
- `C(t)`: syndrome classification
- `B(t)`: biomarker vector
- `M(t)`: comorbidity burden
- `R(t)`: treatment response state

All modules contribute to computing `P_snapshot(t_now)` and its derivative objects (risk scores, confidence vector, conflict set, version history).

---

## 1. Common Module Contract

All algorithm modules must conform to a shared abstract interface.

### 1.1 Input Context

Each module receives a **read-only view** of:

- `L_sub`: Subset of `EvidenceLedgerEvent` objects for a given `subject_id`, filtered to `observation_timestamp <= t_eval`.
- `config`: Module-specific configuration object (thresholds, mapping tables, priors).
- `nosology_version`: Active `NosologyVersion` identifier (e.g., `ILAE-2025`).
- `algorithm_version`: Active `AlgorithmVersion` identifier (e.g., `VLEP-0.1.0`).

### 1.2 Output Contract

Each module returns a **typed result object**:

```jsonc
{
  "module_id": "seizure_classification_v0_1_0",
  "subject_id": "pseudonymous-uuid",
  "t_eval": "ISO8601",
  "primary_assertion": {            // optional for meta-modules
    "assertion_type": "seizure_type",
    "value": "focal_impaired_awareness",
    "value_code": {"system": "ILAE-2025", "code": "FIA"},
    "confidence": 0.83,
    "supporting_ledger_events": ["evt-1", "evt-2"],
    "contradicting_ledger_events": ["evt-9"],
    "algorithm_version": "VLEP-0.1.0",
    "nosology_version": "ILAE-2025"
  },
  "auxiliary_assertions": [         // e.g., subtype probabilities
    { "assertion_type": "seizure_subtype_probability", ... }
  ],
  "diagnostic_notes": [             // machine-readable notes for reviewers
    "Insufficient EEG evidence for generalized onset; defaulted to clinical semiology.",
    "Conflicting diary vs. ED note on awareness impairment."
  ]
}
```

Meta-modules (risk, confidence, conflict, versioning) may return `primary_assertion = null` and populate module-specific fields.

---

## 2. Seizure Classification Module

**Module ID:** `seizure_classification_v0_1_0`  
**Purpose:** Map ledger evidence to **seizure type cluster** \(S(t)\) and subtype probabilities under the active ILAE nosology.

### 2.1 Inputs

- Domains from `EvidenceLedgerEvent.data_element.domain`:
  - `seizure_semiology`
  - `seizure_onset`
  - `seizure_awareness`
  - `seizure_motor_features`
  - `diagnostic_finding` (EEG seizure patterns)
  - `trigger` (for reflex epilepsies, as secondary)

### 2.2 Deterministic Logic (v0.1)

1. **Event aggregation**:
   - Collect all seizure-related events within a lookback window `W_seizure` (e.g., last 24 months) and with `certainty >= τ_min`.
   - Weight events by recency using an exponential decay kernel `exp(-λ_seizure * Δt)`.

2. **ILAE feature extraction**:
   - Derive features:
     - Onset: `focal | generalized | unknown`.
     - Awareness: `impaired | retained | unknown`.
     - Motor: `motor | nonmotor`.
     - EEG pattern: e.g., `3Hz_GSW`, `irregular_spike_wave`, `focal_IED`.

3. **Rule-based mapping** to ILAE seizure types (non-exhaustive examples):

   - If majority of high-certainty EEG events show generalized spike–wave (e.g., `3Hz_GSW`) **and** clinical description mentions absence spells → classify as `generalized_nonmotor_absence`.
   - If onset clearly focal (auras, automatisms, unilateral motor signs) with impaired awareness → `focal_impaired_awareness`.
   - If convulsive seizures with unknown onset and no clear focal signs → `unknown_onset_tonic_clonic`.

4. **Probability assignment**:
   - Use normalized vote weighting across rules and evidence sources:
     - Clinical notes votes
     - EEG-confirmed events votes
     - Patient diary votes (down-weighted)
   - Compute \( p_k \) for each candidate seizure type \(k\); select argmax as `primary_assertion.value` and store full distribution in `auxiliary_assertions`.

5. **Edge cases**:
   - If evidence insufficient or heavily conflicting → set `value = "unclassified"`, `confidence <= 0.4`, and emit a diagnostic note.

### 2.3 Outputs

- `PhenotypeAssertion` of type `seizure_type` with subtype ILAE code.
- Optional `seizure_subtype_probability` assertions for downstream risk models.

---

## 3. Etiology Module

**Module ID:** `etiology_module_v0_1_0`  
**Purpose:** Assign the **etiology class** \(E(t)\): `genetic, structural, infectious, metabolic, immune, traumatic, post_surgical, unknown`.

### 3.1 Inputs

- Ledger domains:
  - `etiology`
  - `genetic_finding`
  - `diagnostic_finding` (MRI/CT, PET, structural lesions)
  - `lab_result` (metabolic markers)
  - `immunologic_marker`
  - `clinical_history` (trauma, infection, perinatal insult)

### 3.2 Deterministic Logic (Hierarchy)

The module applies a **hierarchical precedence** consistent with ILAE recommendations and project literature:

1. **Genetic**:
   - Pathogenic/likely pathogenic variants in curated epilepsy gene list (e.g., SCN1A, KCNQ2, DEPDC5) with strong literature support (Tier 1–2) → `genetic`.
   - De novo variants in DEE genes with established association → `genetic`.

2. **Structural**:
   - Imaging-confirmed cortical dysplasia, hippocampal sclerosis, tumors, vascular malformations, malformations of cortical development → `structural`.

3. **Infectious**:
   - Documented CNS infection temporally linked to onset (e.g., encephalitis, neurocysticercosis) → `infectious`.

4. **Metabolic**:
   - Confirmed inborn errors of metabolism, GLUT1 deficiency, mitochondrial disorders with documented seizures → `metabolic`.

5. **Immune**:
   - Autoimmune encephalitis, neuronal autoantibodies, steroid-responsive epilepsies → `immune`.

6. **Traumatic**:
   - Moderate–severe TBI or neurosurgical insult with subsequent epilepsy → `traumatic`.

7. **Post-surgical**:
   - Epilepsy developing after resective surgery for another pathology → `post_surgical`.

8. **Unknown**:
   - No adequate evidence for above classes.

The module must:

- Allow **multi-etiology** flags (e.g., `genetic + structural`) but still output a primary class plus secondary tags.
- Attach **supporting_ledger_events** for each contributing evidence item.

### 3.3 Outputs

- `PhenotypeAssertion` of type `etiology` (primary value + confidence).
- Optional `etiology_secondary` assertions (e.g., `structural_tag` for `genetic+structural`).

---

## 4. Syndrome Module

**Module ID:** `syndrome_module_v0_1_0`  
**Purpose:** Apply **age- and etiology-aware syndrome definitions** \(C(t)\) under the active `NosologyVersion`.

### 4.1 Inputs

- Outputs from: Seizure, Etiology, and Biomarker modules.
- Ledger domains:
  - `syndrome` (explicit clinical labels)
  - `age_at_onset`
  - `developmental_course`
  - `EEG_pattern`
  - `imaging_finding`

### 4.2 Deterministic Logic (Examples)

1. **West syndrome**:
   - Infantile spasms (clustered flexor/extensor spasms) **and** hypsarrhythmia on EEG **and** onset < 2 years.

2. **Lennox–Gastaut syndrome**:
   - Multiple seizure types including tonic and atypical absences **and** slow spike-and-wave (1.5–2.5 Hz) on EEG **and** onset in childhood.

3. **Dravet syndrome**:
   - Prolonged febrile hemiclonic or generalized seizures in the first year of life **plus** pathogenic SCN1A variant **plus** later emergence of multiple seizure types and developmental plateau.

4. **Genetic generalized epilepsy**:
   - Absence, myoclonic, and/or generalized tonic–clonic seizures with generalized spike–wave, normal MRI, and no focal lesion.

The module must:

- Implement a **rule set** for initial high-prevalence syndromes (West, LGS, Dravet, GGE, TLE, etc.).
- Compute a **confidence score** based on the completeness of required features and supporting Tier 1–2 literature claims.
- Defer to `unknown_syndrome` when criteria partially met or conflicting.

### 4.3 Outputs

- `PhenotypeAssertion` of type `syndrome` with nosology code.
- `diagnostic_notes` describing which criteria were satisfied or missing.

---

## 5. Biomarker Module

**Module ID:** `biomarker_module_v0_1_0`  
**Purpose:** Aggregate EEG, imaging, and genetic biomarkers into the **biomarker vector** \(B(t)\) and expose them as structured assertions.

### 5.1 Inputs

- Ledger domains:
  - `eeg_finding` (interictal spikes, HFOs, background slowing, seizure onset zone)
  - `eeg_quantitative_metric` (spike rate, spectral power)
  - `imaging_finding` (lesion location, malformations, hippocampal sclerosis)
  - `genetic_finding` (variant-level)

### 5.2 Deterministic Logic

- EEG:
  - Normalize spike rates per unit time and classify as `none`, `low`, `moderate`, `high` burden.
  - Flag presence of HFOs, generalized vs. focal IEDs, background slowing.
- Imaging:
  - Normalize reported findings to structured vocabulary (e.g., `mesial_temporal_sclerosis`, `focal_cortical_dysplasia_type_II`).
- Genetics:
  - Map variants to a curated tiering: `pathogenic`, `likely_pathogenic`, `VUS`, `likely_benign`, `benign`.

### 5.3 Outputs

- Multiple `PhenotypeAssertion` objects of type `biomarker_finding` (EEG, imaging, genetic) with severity/qualifiers.
- A summary `biomarker_vector` structure attached inside the CSEP.

---

## 6. Treatment-Response Module

**Module ID:** `treatment_response_module_v0_1_0`  
**Purpose:** Classify **treatment response state** \(R(t)\): `drug_responsive`, `emerging_resistance`, `pharmacoresistant`, `insufficient_data`.

### 6.1 Inputs

- Ledger domains:
  - `medication_trial` (drug, dose, start/stop, adherence)
  - `seizure_frequency`
  - `outcome` (seizure-free intervals)
  - `adverse_event`

### 6.2 Deterministic Logic

Use ILAE-style rules plus DRE literature:

1. Compute **trials of adequately dosed ASMs** with good adherence.
2. For each trial, assess **response**:
   - Seizure-free ≥ 12 months or 3× pre-treatment inter-seizure interval → `responsive`.
   - Partial reduction without seizure freedom → `partial`.
   - No meaningful change or worsening → `nonresponsive`.
3. Treatment state classification:
   - If current ASM yields sustained seizure freedom → `drug_responsive`.
   - If ≥ 1 failed adequate ASM and current response deteriorating over last 6–12 months → `emerging_resistance`.
   - If ≥ 2 failed adequate ASMs (per ILAE definition) → `pharmacoresistant`.
   - If data sparse or inconsistent → `insufficient_data`.

### 6.3 Outputs

- `PhenotypeAssertion` of type `treatment_response` with effective date and confidence.
- Auxiliary assertions about each individual ASM trial.

---

## 7. Comorbidity Module

**Module ID:** `comorbidity_module_v0_1_0`  
**Purpose:** Compute **comorbidity burden** \(M(t)\) across psychiatric, cognitive, behavioral, developmental, sleep, and medical domains.

### 7.1 Inputs

- Ledger domains:
  - `comorbidity_diagnosis` (ICD codes mapped to categories)
  - `neuropsychology_result`
  - `psychiatric_assessment`
  - `sleep_assessment`
  - `patient_reported_outcome`

### 7.2 Deterministic Logic

- Map diagnoses into burden scores per domain (e.g., none/mild/moderate/severe).
- Incorporate standardized scales (e.g., PHQ-9, GAD-7, IQ scores) where available.
- Apply temporal decay so that **resolved** comorbidities gradually reduce burden.

### 7.3 Outputs

- `PhenotypeAssertion` of type `comorbidity` with domain-specific subfields.
- A compact `comorbidity_profile` embedded in the CSEP.

---

## 8. Risk Module

**Module ID:** `risk_module_v0_1_0`  
**Purpose:** Compute risk scores derived from phenotype and trajectory: **DRE risk**, **SUDEP risk burden**, and **seizure burden trend**.

### 8.1 Inputs

- Outputs from: Seizure, Etiology, Syndrome, Biomarker, Treatment-Response, Comorbidity modules.
- Longitudinal seizure counts from ledger.

### 8.2 Deterministic Logic (Examples)

1. **DRE risk logistic model** (as in mainframe spec):

   - Predictors: first ASM response, log baseline seizure frequency, MRI lesion presence, developmental encephalopathy indicator, cognitive impairment, time since diagnosis.
   - Fixed coefficients initially from literature; later updated by calibration.

2. **Seizure burden trend**:
   - Fit a simple Poisson or negative binomial regression over time windows to classify trend as `increasing`, `decreasing`, `stable`, or `insufficient_data`.

3. **SUDEP risk burden** (rule-based v0.1):
   - Aggregate known factors: nocturnal generalized tonic–clonic seizures, high frequency of convulsive seizures, prone sleep position, treatment nonadherence, comorbid intellectual disability, etc.
   - Output a categorical risk bucket (`low`, `moderate`, `high`) with supporting factors.

### 8.3 Outputs

- `RiskScore` objects attached to CSEP.
- Optional `PhenotypeAssertion` of type `risk_factor` for individual risk contributors.

---

## 9. Confidence Module

**Module ID:** `confidence_module_v0_1_0`  
**Purpose:** Compute per-domain **confidence scores** based on data density, recency, internal consistency, and source quality.

### 9.1 Inputs

- All `PhenotypeAssertion` outputs.
- Ledger-derived metrics: number of events per domain, time since last event, fraction of Tier 1–2 evidence sources.

### 9.2 Deterministic Logic

For each domain \(d \in \{S, E, C, B, M, R\}\):

- Initialize base confidence from **evidence tiering** (Tier 1 > Tier 2 > Tier 3 > unstructured).
- Apply multiplicative modifiers:
  - **Data density**: more consistent observations → higher confidence.
  - **Recency**: recent observations increase, stale data decreases.
  - **Conflict**: contradictions reduce confidence.

Return a `confidence_vector` with values in `[0,1]` per domain.

---

## 10. Conflict Module

**Module ID:** `conflict_module_v0_1_0`  
**Purpose:** Identify and structure **contradictory evidence** within the ledger and across module outputs.

### 10.1 Inputs

- Ledger events grouped by subject and domain.
- All module assertions.

### 10.2 Deterministic Logic

- Define **conflict rules**, e.g.:
  - Seizure type labeled `focal` in one high-certainty note vs. `generalized` in EEG report.
  - Etiology `genetic` with no documented pathogenic variant vs. `structural` with clear lesion.
  - Treatment response `pharmacoresistant` while recent seizure logs indicate prolonged seizure freedom.

- For each conflict, create a `ConflictRecord`:

```jsonc
{
  "conflict_id": "uuid",
  "subject_id": "pseudonymous-uuid",
  "domain": "seizure_type",
  "evidence_a_events": ["evt-1", "evt-5"],
  "evidence_b_events": ["evt-7"],
  "severity": "minor | moderate | major",
  "detected_by": "conflict_module_v0_1_0"
}
```

- Mark affected assertions with references to `conflict_id` in `contradiction_flags`.

### 10.3 Outputs

- A list of `ConflictRecord` objects for reviewer queues.

---

## 11. Versioning Module

**Module ID:** `versioning_module_v0_1_0`  
**Purpose:** Coordinate **recomputation** of CSEP and assertions when the nosology or algorithm versions change.

### 11.1 Inputs

- `NosologyVersion` registry.
- `AlgorithmVersion` registry.
- Current and prior CSEP snapshots.

### 11.2 Deterministic Logic

- Detect events:
  - New `nosology_version` activated.
  - New `algorithm_version` released for a module.

- For each affected subject:
  - Flag CSEP as `requires_recomputation`.
  - Schedule re-run of all or selected modules under new versions.
  - Capture `version_history` link between old and new CSEP IDs.

### 11.3 Outputs

- Updated `CurrentStateEpilepsyProfile.version_history` chains.
- `ReviewerDecision` tasks when major phenotype shifts occur after recomputation.

---

## 12. Implementation Notes for v0.1

- v0.1 should prioritize **interpretable, rule-based logic** using the 239 curated literature claims as hard or soft constraints rather than opaque ML.
- All thresholds (e.g., window sizes, decay rates, cutoffs for DRE risk buckets) must be stored in configuration and versioned.
- Each module implementation should live under `algorithm/modules/<module_name>/` with:
  - `spec.md` (this document, subdivided if needed)
  - `rules.yaml` (data-driven rule tables)
  - `module.py` (reference implementation)
- Unit tests in `tests/algorithm/modules/` must cover edge cases and round-trip audibility (ledger → assertion → human-readable explanation).

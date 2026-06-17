# VLEP Study Protocol — Longitudinal Epilepsy Phenotyping

**Version:** 1.0  
**Status:** Active  
**Date:** 2025

---

## 1. Study Objectives

**Primary:** Validate the VLEP framework for longitudinal epilepsy phenotype
classification against retrospective clinical records.

**Secondary:**
- Assess CSEP resolver accuracy against expert clinician classification
- Validate the DRE risk model against observed DRE outcomes
- Benchmark HMM latent state trajectories against disease course narratives

---

## 2. Inclusion Criteria

- Confirmed epilepsy diagnosis (ILAE 2017 criteria)
- ≥2 clinical encounters in the dataset
- ≥1 EEG or neuroimaging record available
- Age 0–85 years at index date

## 3. Exclusion Criteria

- Isolated provoked seizures without epilepsy diagnosis
- Single encounter records only (insufficient for longitudinal analysis)
- Missing demographic data (age at onset, sex)

---

## 4. Data Sources

| Source | Tier | Contents |
|--------|------|----------|
| Epileptologist visit notes | T1 | Semiology, ASM changes, response assessment |
| EEG reports | T1 | Interictal/ictal patterns, classification |
| MRI reports | T1 | Structural lesions, hippocampal sclerosis |
| Genetic panels | T1 | Pathogenic variant identification |
| Claims/billing records | T3 | ICD-10 codes, prescription history |
| Patient questionnaires | T3 | Seizure diaries, QoL scales |

---

## 5. Data Processing Pipeline

1. **Ingestion** — Records loaded via `LPAEngine.ingest()`
2. **Tiering** — Source classified as T1/T2/T3 via `ProvenanceTierer`
3. **NLP Extraction** — Claims extracted via `NLPExtractionPipeline`
4. **Ledger Append** — Immutable `EvidenceLedger` updated
5. **CSEP Resolution** — `CSEPResolver.resolve()` produces phenotype profile
6. **Model Inference** — HMM, GLMM, Survival models update predictions
7. **Report Export** — `LPAEngine.export_summary()` produces structured JSON

---

## 6. Validation Approach

### CSEP Accuracy
- Gold standard: expert epileptologist classification at each time point
- Metric: Cohen's κ for categorical dimensions; Pearson r for continuous

### DRE Risk Model
- Gold standard: observed DRE outcome at 24 months
- Metrics: AUROC, Brier score, C-index

### HMM State Recovery
- Gold standard: clinician-labeled disease phase (remission / partial / DRE)
- Metrics: State classification accuracy, F1 per state

---

## 7. Ethical Considerations

All patient data must be de-identified per HIPAA Safe Harbor before ingestion.
The evidence ledger retains full audit trails for clinical governance review.
Algorithm outputs are decision-support tools and do not replace clinical judgment.

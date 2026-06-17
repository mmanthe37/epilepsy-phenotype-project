# Implementation Roadmap

## Phase 1 — Core Algorithm (Complete)

- [x] Phenotype vector specification (P(t) six-dimensional)
- [x] Evidence ledger with SHA-256 integrity
- [x] Temporal decay engine
- [x] Provenance tiering (T1/T2/T3)
- [x] NLP extraction pipeline
- [x] CSEP resolver
- [x] LPA orchestration engine
- [x] HMM (5 latent states)
- [x] GLMM longitudinal model
- [x] Survival ensemble
- [x] GP imputation
- [x] DRE risk classifier
- [x] Ontology embeddings
- [x] Validation metrics (td-AUROC, C-index, Brier)
- [x] Versioning / nosological framework (ILAE 2010→2025)

## Phase 2 — Data Integration

- [ ] FHIR R4 ingestion adapter
- [ ] ICD-10 → VLEP phenotype mapping tables
- [ ] EEG report structured extraction
- [ ] Genetic variant annotation (ClinVar, OMIM)
- [ ] Pharmacy claims ASM mapping

## Phase 3 — Validation Study

- [ ] IRB approval for retrospective chart review
- [ ] Pilot dataset (100 patients, 3+ years follow-up)
- [ ] CSEP accuracy validation against expert annotation
- [ ] DRE risk model calibration
- [ ] External validation cohort

## Phase 4 — Clinical Integration

- [ ] REDCap integration for prospective data entry
- [ ] Clinical dashboard (React + REST API)
- [ ] EHR alert integration for DRE risk flagging
- [ ] Automated CSEP report generation in PDF/FHIR

## Phase 5 — Publication & Dissemination

- [ ] Methods paper submission (Epilepsia / Journal of Neurology)
- [ ] Algorithm preprint (medRxiv)
- [ ] Open-source release with de-identified demonstration dataset
- [ ] Conference presentation (AES Annual Meeting)

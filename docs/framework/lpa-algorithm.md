# Longitudinal Phenotyping Algorithm (LPA) — Technical Reference

## Overview

The **Longitudinal Phenotyping Algorithm (LPA)** is the computational engine
that ingests multi-modal clinical data, maintains the VLEP evidence ledger,
and produces CSEP (Current State Epilepsy Profile) reports across time.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        LPA ENGINE                               │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  NLP Extract │───▶│   Evidence   │───▶│   CSEP Resolver  │  │
│  │   Pipeline   │    │    Ledger    │    │                  │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│         │                                        │              │
│  ┌──────▼───────┐    ┌──────────────┐    ┌──────▼───────────┐  │
│  │  Provenance  │    │  Temporal    │    │    HMM / GLMM /  │  │
│  │   Tiering    │    │    Decay     │    │  Survival Ensem. │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Summary

| Component | Module | Function |
|-----------|--------|----------|
| Ingestion | `lpa_engine.py` | Accepts records, routes to NLP + Tiering |
| NLP Extraction | `nlp_extraction.py` | Extracts 239 phenotype-defining claims |
| Provenance Tiering | `provenance_tiering.py` | Classifies source tier (T1/T2/T3) |
| Evidence Ledger | `evidence_ledger.py` | Immutable append-only ledger |
| Temporal Decay | `temporal_decay.py` | δ(t,tₖ;γ) = e^(−γ(t−tₖ)) |
| CSEP Resolver | `csep_resolver.py` | CSEP(t) = argmax posterior estimate |
| HMM | `hmm.py` | Latent phenotype state sequence |
| GLMM | `glmm.py` | Longitudinal seizure frequency model |
| Survival Ensemble | `survival_ensemble.py` | DRE onset hazard prediction |
| GP Imputation | `gp_imputation.py` | Missing data interpolation (Matérn GP) |
| DRE Risk Model | `dre_risk_model.py` | Binary pharmacoresistance classifier |

---

## CLI Usage

```bash
# Run the built-in demonstration
python -m algorithm.core.lpa_engine --demo

# Ingest a claims file
python -m algorithm.core.lpa_engine --ingest path/to/claims.csv
```

---

## Output Format

CSEP report fields:

```json
{
  "patient_id": "PT-001",
  "resolved_at": "2024-01-15T09:00:00",
  "phenotype_dimensions": {
    "seizure_type": "focal_impaired_awareness",
    "etiology": "structural",
    "syndrome": "mesial_tle",
    "treatment_response": "drug_responsive"
  },
  "confidence_scores": {"seizure_type": 0.91, "etiology": 0.87},
  "clinical_flags": ["high_seizure_burden", "mri_lesion_detected"],
  "dre_risk_score": 0.34,
  "narrative": "..."
}
```

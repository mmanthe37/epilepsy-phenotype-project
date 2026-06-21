# VLEP Canonical Data Model
## Core Data Objects and Schema Definitions

**Version:** 0.1.0  
**Date:** 2026-06-21  

---

## Core Data Objects

### Subject
```json
{
  "subject_id": "pseudonymous-uuid",
  "enrollment_date": "YYYY-MM-DD",
  "consent_status": "active | withdrawn | pending",
  "study_cohort": "string",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

### ConsentRecord
```json
{
  "consent_id": "uuid",
  "subject_id": "pseudonymous-uuid",
  "consent_type": "research_participation | data_use | biobanking | contact",
  "status": "active | withdrawn | expired",
  "consent_date": "YYYY-MM-DD",
  "withdrawal_date": "YYYY-MM-DD | null",
  "data_uses_permitted": ["aggregate_research", "model_training", "publication"]
}
```

### SourceDocument
```json
{
  "document_id": "uuid",
  "subject_id": "pseudonymous-uuid",
  "document_type": "clinician_note | eeg_report | mri_report | genetic_report | discharge_summary | seizure_diary | lab_report | neuropsych_report | patient_upload",
  "source_date": "YYYY-MM-DD",
  "upload_timestamp": "ISO8601",
  "raw_storage_path": "s3://...",
  "processing_status": "pending | processed | failed",
  "provenance": {
    "origin": "patient_upload | ehr_import | manual_entry | fhir_feed",
    "institution": "string | null"
  }
}
```

### EvidenceLedgerEvent
```json
{
  "ledger_event_id": "uuid",
  "subject_id": "pseudonymous-uuid",
  "observation_timestamp": "ISO8601",
  "ingestion_timestamp": "ISO8601",
  "data_element": {
    "domain": "seizure_semiology | etiology | syndrome | biomarker | medication | comorbidity | diagnostic_finding | trigger | outcome",
    "subdomain": "string",
    "value": "string",
    "coded_terms": [
      { "system": "ILAE | ICD-11 | SNOMED | RxNorm | LOINC", "code": "string", "display": "string" }
    ],
    "raw_text": "string | null"
  },
  "source_document_id": "uuid",
  "audit_metadata": {
    "certainty": 0.0,
    "validation_status": "unreviewed | reviewed | validated | rejected",
    "extraction_method": "nlp_v1.3 | manual_entry | fhir_import",
    "reviewer_id": "uuid | null",
    "reviewed_at": "ISO8601 | null"
  },
  "classification_version": {
    "nosology_version": "ILAE-2025",
    "algorithm_version": "VLEP-0.1.0"
  },
  "hash": "sha256-hex",
  "previous_hash": "sha256-hex | null"
}
```

### PhenotypeAssertion
```json
{
  "assertion_id": "uuid",
  "subject_id": "pseudonymous-uuid",
  "assertion_type": "seizure_type | epilepsy_type | syndrome | etiology | treatment_response | comorbidity | risk_factor | biomarker_finding",
  "value": "string",
  "value_code": { "system": "string", "code": "string" },
  "confidence": 0.0,
  "effective_start": "YYYY-MM-DD",
  "effective_end": "YYYY-MM-DD | null",
  "supporting_ledger_events": ["uuid"],
  "contradicting_ledger_events": ["uuid"],
  "algorithm_version": "VLEP-0.1.0",
  "nosology_version": "ILAE-2025",
  "review_status": "pending_expert_review | approved | rejected",
  "reviewer_id": "uuid | null",
  "reviewed_at": "ISO8601 | null"
}
```

### CurrentStateEpilepsyProfile (CSEP)
```json
{
  "csep_id": "uuid",
  "subject_id": "pseudonymous-uuid",
  "snapshot_timestamp": "ISO8601",
  "algorithm_version": "VLEP-0.1.0",
  "nosology_version": "ILAE-2025",
  "phenotype_vector": {
    "seizure_type": { "value": "string", "confidence": 0.0, "assertion_id": "uuid" },
    "epilepsy_type": { "value": "string", "confidence": 0.0, "assertion_id": "uuid" },
    "syndrome": { "value": "string", "confidence": 0.0, "assertion_id": "uuid" },
    "etiology": { "value": "string", "confidence": 0.0, "assertion_id": "uuid" },
    "biomarkers": { "eeg_findings": [], "imaging_findings": [], "genetic_findings": [] },
    "treatment_response": { "value": "string", "confidence": 0.0, "assertion_id": "uuid" },
    "comorbidity_burden": { "psychiatric": null, "cognitive": null, "behavioral": null, "sleep": null }
  },
  "risk_scores": {
    "dre_probability": 0.0,
    "sudep_risk_burden": 0.0,
    "seizure_burden_trend": "stable | increasing | decreasing | insufficient_data"
  },
  "confidence_vector": {
    "seizure_type": 0.0, "etiology": 0.0, "syndrome": 0.0,
    "treatment_response": 0.0, "comorbidity": 0.0, "biomarkers": 0.0
  },
  "review_status": "unreviewed | clinician_reviewed | validated | rejected",
  "version_history": ["previous-csep-id"],
  "active_assertions": ["uuid"],
  "contradiction_flags": ["uuid"]
}
```

### NosologyVersion
```json
{
  "nosology_version_id": "ILAE-2025",
  "display_name": "ILAE Epilepsy Classification 2025",
  "effective_date": "2025-01-01",
  "supersedes": "ILAE-2017",
  "specification_url": "https://...",
  "seizure_type_definitions": {},
  "syndrome_definitions": {},
  "etiology_definitions": {}
}
```

### AlgorithmVersion
```json
{
  "algorithm_version_id": "VLEP-0.1.0",
  "release_date": "2026-06-21",
  "description": "Initial deterministic phenotype computation engine",
  "supported_nosology_versions": ["ILAE-2025"],
  "modules": [
    "seizure_classification", "etiology", "syndrome", "biomarker",
    "treatment_response", "comorbidity", "risk", "confidence", "conflict", "versioning"
  ],
  "changelog": "Initial specification"
}
```

### PublicMetric
```json
{
  "metric_id": "uuid",
  "metric_name": "string",
  "metric_category": "system_activity | data_completeness | phenotype_distribution | model_performance | versioning | research_progress",
  "value": 0.0,
  "unit": "string",
  "computed_at": "ISO8601",
  "published_at": "ISO8601",
  "suppressed": false,
  "suppression_reason": "null | small_count | rare_combination"
}
```

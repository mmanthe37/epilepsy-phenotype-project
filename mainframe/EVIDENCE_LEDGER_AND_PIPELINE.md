# Evidence Ledger, Ingestion, and Governance Specification

**Project:** Epilepsy Phenotype Project  
**Component:** Immutable Evidence Ledger and Data Pipeline  
**File:** `mainframe/EVIDENCE_LEDGER_AND_PIPELINE.md`  
**Version:** 0.1.0  
**Status:** Normative design spec for research prototype (non-clinical)

> ⚠️ This document defines a **research** data platform. It must not be deployed as a diagnostic system or used to make individual clinical decisions without IRB approval, regulatory review, and formal clinical validation.

---

## 1. Purpose and Design Principles

This specification operationalizes the VLEP tuple \(VLEP = (L, N, F, P_{snapshot})\) by defining:

- The **immutable evidence ledger** \(L\) and append-only event schema.  
- The **data ingestion and normalization pipeline** from raw sources into standardized clinical data elements.  
- **HIPAA-style safeguards**, privacy controls, and governance structures.  
- Developer-facing **implementation rules** that prevent violations of immutability, provenance, or PHI-handling constraints.

Foundational principles (derived from the theoretical VLEP framework and implementation roadmap):

1. **Immutability:** No clinical observation is ever edited or deleted once committed; all corrections are new, linked events.[cite:44][cite:46]
2. **Auditability:** Every derived phenotype assertion must be traceable to specific ledger events and, for literature priors, to concrete PubMed/PMC sentences.[cite:19][cite:42]
3. **Versioning:** Reinterpretation occurs only through new CSEP snapshots under updated nosology or algorithm versions; historical ledger content remains fixed.[cite:44][cite:46]
4. **Minimum necessary PHI:** Identifiers are segregated, pseudonymous IDs are used in the ledger, and only the minimum fields required for research or CDS are exposed.[cite:44][cite:40]
5. **Evidence tiering:** Only rigorously graded Tier 1–2 literature claims can influence safety-critical outputs or interruptive alerts.[cite:19][cite:42]
6. **Governed change:** All changes to ingestion rules, ledger schema, or algorithms must be reviewable by the governance triad (ESC, OTB, CAEG) before affecting live data.[cite:40]

---

## 2. Data Source Registry and Intake Rules

### 2.1 Source Types

All ingestible inputs are registered in a **Source Registry** with metadata (ownership, legal basis, consent scope, PHI content, refresh cadence).[cite:46]

Primary clinical sources:

- EHR data via FHIR R4 (USCDI v3) and HL7 v2 feeds (ADT^A01, ORU^R01).[cite:40][cite:46]
- Neurology and epilepsy clinic notes (structured templates when available).[cite:44]
- EEG reports and raw EEG segment metadata.
- Neuroimaging reports and structured imaging findings.
- Medication orders, dispenses, and adherence data.
- Lab and metabolic panels (LOINC-mapped).[cite:42]
- Neuropsychological assessments and comorbidity instruments (PHQ‑9, GAD‑7, etc.).[cite:44]
- Patient- and caregiver-reported outcomes (seizure diaries, triggers, sleep, stress).[cite:21]

Secondary knowledge sources:

- Biomedical literature via PubMed and PMC Open Access, ingested through E-Utilities and REST APIs.[cite:19][cite:42]
- Clinical guidelines (ILAE, AES, AAN) and consensus statements.[cite:21][cite:42]

### 2.2 Intake Services

Intake is implemented via dedicated services:[cite:46]

- **Upload Service:** Accepts PDFs, text, CSV, EEG exports, and imaging reports; performs virus scanning and file-type whitelisting.  
- **FHIR Connector:** Pulls structured clinical data using OAuth 2.0–secured SMART on FHIR sessions.[cite:40]  
- **HL7 Listener:** Receives real-time ADT/ORU events over VPN/IPsec from interface engines.[cite:40]  
- **Diary API:** Authenticated endpoints for patients to submit seizure counts, triggers, and PROs.  
- **Document Parser:** OCR and text extraction for scanned reports.  
- **Source Registry Service:** Stores per-source configuration, including allowed data elements and PHI classification.[cite:46]

**Rule:** No data bypasses the Source Registry. Unregistered sources must not be ingested into the ledger.

---

## 3. Normalization, De‑Identification, and CDE Mapping

### 3.1 Terminology and CDE Alignment

A **Normalization Service** converts raw text and structured fields into standardized data elements aligned with:

- ILAE 2025 seizure and epilepsy classifications.[cite:21][cite:44]
- NINDS Epilepsy Common Data Elements (seizure characterization, etiology, treatment, outcomes, diagnostics).[cite:44]
- HPO for phenotypic traits, SNOMED‑CT for diagnoses, RxNorm for medications, LOINC for labs.[cite:42]

Key tasks:

- NLP extraction of seizure semiology, EEG findings, imaging results, medications, and comorbidities from free text using transformer models (e.g., BioClinicalBERT).[cite:19][cite:42]
- Mapping of fields to epilepsy-specific CDE schemas (e.g., `seizure_onset`, `etiology_category`, `medication_trial`).[cite:44]
- Temporal normalization (observation timestamps, date ranges) and time-zone handling.

### 3.2 De‑Identification Pipeline

For research and public analytics environments:

- Direct identifiers (names, MRNs, addresses, full dates of birth) are removed or tokenized.
- Pseudonymous `subject_id` replaces local identifiers; a separate, access-controlled linkage table resides outside research environments.[cite:44][cite:46]
- Free-text fields are scrubbed using PHI-detection NLP and pattern matching.
- Date shifting or coarse-graining (e.g., month/year only) is applied where necessary to meet re-identification risk thresholds.[cite:44]

**Rule:** No raw PHI crosses from the clinical integration boundary into research sandboxes or public dashboards; only de-identified or aggregate data may be exported.[cite:40][cite:46]

### 3.3 Data Quality and Plausibility Checks

A **Quality Validator** enforces:[cite:44][cite:46]

- Range and type checks (e.g., impossible ages, negative seizure counts).  
- Temporal consistency (e.g., seizure dates not preceding date of birth).  
- Cross-field plausibility (e.g., generalized-only EEG with focal-only syndrome label triggers a contradiction flag).  
- Missingness indicators for downstream confidence computation.

Invalid or ambiguous records are logged and optionally routed to a manual curation queue; they are still ingested but clearly marked with low certainty.

---

## 4. Immutable Evidence Ledger (L)

### 4.1 Conceptual Definition

The ledger is an append-only event store:

\[ L = \{ (t_i, D_i, s_i, a_i, v_i) \}_{i=1..n} \]

where each tuple encodes: observation time, data element, source attribution, audit metadata, and classification version.[cite:44]

No operation may mutate or delete an existing ledger event. All corrections, re-interpretations, or re-annotations are represented as **new events** that reference earlier ones via explicit linkage fields.[cite:46]

### 4.2 Event Schema (Normative)

Each `EvidenceLedgerEvent` must conform to:

```jsonc
{
  "ledger_event_id": "uuid",               // immutable primary key
  "subject_id": "pseudonymous-id",         // no direct PHI
  "observation_timestamp": "ISO8601",      // when the observation occurred
  "ingestion_timestamp": "ISO8601",        // when the system ingested it
  "data_element": {
    "domain": "seizure_semiology | eeg_finding | imaging_finding | genetic_finding | medication_trial | comorbidity | lab_result | trigger | outcome | device_upload | other",
    "cde_code": "NINDS-EPI-...",           // optional
    "value": {},                            // typed value (string/number/object)
    "raw_text_excerpt": "...",             // de-identified snippet when available
    "coded_terms": [                        // mapped terminologies
      {"system": "SNOMED-CT", "code": "..."},
      {"system": "HPO", "code": "..."}
    ]
  },
  "source": {
    "source_type": "ehr | clinician_note | patient_report | device | literature | registry",
    "facility_id": "...",
    "document_or_message_id": "...",
    "author_role": "neurologist | epileptologist | patient | system",
    "acquisition_channel": "FHIR | HL7v2 | upload | api"
  },
  "audit_metadata": {
    "certainty": 0.0,
    "validation_status": "unreviewed | reviewer_validated | reviewer_rejected",
    "extraction_method": "manual | nlp_bioclinnbert_vX | import_script_vY",
    "notes": "..."
  },
  "classification_version": {
    "nosology_version": "ILAE-2025",
    "algorithm_version": "VLEP-0.1.0"
  },
  "links": {
    "corrects_event_ids": ["uuid-1"],      // for corrections
    "derived_from_event_ids": ["uuid-2"]   // for derived features
  },
  "hash": "sha256-...",                     // event hash
  "previous_hash": "sha256-..."            // prior event hash for chain integrity
}
```

### 4.3 Cryptographic and Operational Guarantees

- **Hash Chain:** Each event’s `hash` includes the `previous_hash` to form a tamper-evident chain.[cite:19][cite:44]
- **Append-Only Storage:** Implemented using write-only append tables or event-store semantics; DDL/ops rules must disallow UPDATE/DELETE on ledger tables except under tightly controlled migration procedures.[cite:46]
- **Immutable Audit Logs:** Access to ledger reads and writes is logged in a separate `AuditEvent` store.[cite:46]

**Developer rule:** No migration, hotfix, or backfill may be performed on ledger tables without a recorded `GovernanceChangeRecord` approved by the ESC and OTB.

---

## 5. End-to-End Pipeline Stages

This section refines the six-stage backend pipeline into normative, implementable stages consistent with the theoretical framework.[cite:44][cite:46]

1. **Source Intake:** Acquire raw data via registered connectors (Section 2).  
2. **Normalization & CDE Mapping:** Extract and standardize fields; assign CDE, terminology codes, and timestamps (Section 3).  
3. **De‑Identification (where applicable):** Apply PHI scrubbing and pseudonymization for research streams (Section 3.2).  
4. **Ledger Commit:** Create `EvidenceLedgerEvent` objects and append to \(L\) with cryptographic hashing (Section 4).  
5. **Phenotype Computation:** Invoke algorithm modules defined in `ALGORITHM_MODULES.md` to generate `PhenotypeAssertion` objects and CSEP snapshots from \(L\).[cite:33][cite:46]  
6. **Review and Publication:** Route outputs through reviewer queues and governance workflows; expose only reviewed or appropriately flagged outputs to portals and APIs.[cite:46][cite:40]

Each stage must be orchestrated in a pipeline framework (e.g., Prefect, Dagster) with explicit run metadata and failure monitoring.[cite:46]

---

## 6. HIPAA-Style Safeguards and Privacy Controls

### 6.1 Technical Safeguards

- **Encryption:** TLS 1.3 for all in-transit connections; AES‑256 for data at rest in databases and object storage.[cite:40][cite:46]
- **Access Control:** Role-based access control (RBAC) with least privilege; MFA required for all privileged roles.[cite:46]
- **Segregated Environments:** Separate development, staging, research, and production environments; PHI permitted only in designated secured environments.[cite:40][cite:46]
- **Audit Logging:** All access to PHI, ledger reads/writes, and model inferences is logged with subject, user, timestamp, and purpose-of-use metadata.[cite:44][cite:46]
- **Secure Upload Scanning:** Uploaded files scanned for malware; restricted MIME types only.[cite:46]

### 6.2 Administrative Safeguards

- **Governance Triad:** ESC (strategic/ROI), OTB (technical stability), CAEG (clinical/ethics) oversee the pipeline, with explicit Go/No-Go checkpoints for each deployment phase.[cite:40]
- **IRB and Data-Use Agreements:** All retrospective and prospective deployments require protocol review and data-use agreements specifying permitted analyses and retention.[cite:44][cite:40]
- **Training:** All developers and analysts must complete HIPAA/security training and sign acceptable-use policies before receiving access.

### 6.3 Data Minimization and Retention

- The ledger stores only necessary clinical observations and metadata; large raw artifacts (e.g., full EEG) live in secured object storage linked by IDs.[cite:44][cite:46]
- Retention schedules are defined per cohort and consent; right-to-withdraw is implemented by revoking linkage between `subject_id` and real-world identifiers, while retaining de-identified ledger events for aggregate research where permitted.[cite:44]

---

## 7. Evidence Tiering and Algorithm Interaction

### 7.1 Literature Evidence Tiers

The literature ingestion engine must classify claims into at least three heuristic tiers using deterministic rules based on study design, cohort size, statistical rigor, and replication density.[cite:19][cite:42]

- **Tier 1:** Guidelines and large RCTs or MR/LDSC-based causal claims. Eligible for active, interruptive safety alerts (e.g., SCN1A/valproate contraindication).[cite:19][cite:42]
- **Tier 2:** Well-powered longitudinal cohorts and validated observational studies. Used for risk estimation and dashboard context, not hard alerts.  
- **Tier 3:** Case reports, small series, and preprints. Available in research views only; never drives automated CDS.[cite:19][cite:42]

Tier labels and weights \(w_i\) are stored on literature-derived `EvidenceLedgerEvent`s and exposed to the algorithm modules as priors.[cite:19]

### 7.2 Interaction with Phenotype Modules

Algorithm modules may consume literature priors only through:

- Explicit lookups of Tier 1–2 claims for specific gene–phenotype, biomarker–risk, or treatment–response relations.  
- Configurable weight matrices \(W\) that modulate GLMM, HMM, or survival ensemble parameters as described in the LPA methods documents.[cite:42][cite:43]

Modules must never query external LLMs or black-box services at runtime for clinical decisions.

---

## 8. Developer and Environment Guidelines

### 8.1 PHI Handling Rules

- **No PHI in development:** Development and unit tests use synthetic or fully de-identified data only.[cite:46]
- **Configuration, not code:** Secrets (DB passwords, API keys, FHIR credentials) must be provided via environment variables or secret managers, not embedded in source control.[cite:46]
- **Logging hygiene:** Logs must not contain PHI, raw clinical notes, or full genetic variants; use event IDs and subject IDs instead.[cite:44]

### 8.2 Schema and API Changes

- Any schema change to `EvidenceLedgerEvent`, `PhenotypeAssertion`, or `CSEP` requires:  
  - A design proposal,  
  - OTB review for technical impact,  
  - CAEG review if semantics touch clinical meaning,  
  - ESC approval if changes impact external commitments.[cite:40]
- Backwards-compatible changes should be preferred (e.g., additive fields, version flags) to preserve ledger interpretability.[cite:46]

### 8.3 Testing and Validation

- **Unit tests:** Must cover ledger immutability, hash-chain integrity, and idempotency of ingestion jobs.[cite:46]
- **Shadow deployments:** New models or inference paths must first run in silent mode against live feeds, with precision/recall targets (e.g., \>0.88/\>0.85) before any clinician-facing activation.[cite:42][cite:40]
- **Equity and bias audits:** CAEG reviews performance across demographic subgroups where available; failing models are restricted to research-only use.[cite:40]

---

## 9. Interfaces to Other Mainframe Components

This specification sits between the **DATA_MODEL**, **ALGORITHM_MODULES**, and mainframe design plan:

- `DATA_MODEL.md` defines the structural objects (`Subject`, `EvidenceLedgerEvent`, `PhenotypeAssertion`, `CSEP`, etc.).[cite:46]
- `ALGORITHM_MODULES.md` defines pure-function modules that consume \(L\) and produce phenotype assertions and risk scores.[cite:33]
- `VLEP_MAINFRAME_DESIGN_PLAN.md` defines the overall architecture, portals, and roadmap; this document concretizes the ingestion, ledger, and governance aspects of that plan.[cite:46]

Implementers must treat this document as **normative** for all code touching the ingestion pipeline, de-identification, ledger, and governance workflows.

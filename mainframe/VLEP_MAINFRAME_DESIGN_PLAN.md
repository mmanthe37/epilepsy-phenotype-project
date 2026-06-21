# VLEP Mainframe Design Plan
## Versioned Longitudinal Epilepsy Phenotype — Multi-Platform Medical Intelligence Ecosystem

**Project:** Epilepsy Profile Phenotype Algorithm and Platform  
**Version:** 0.1.0  
**Date:** 2026-06-21  
**Status:** Architectural Specification — Research Prototype  

> ⚠️ This system is a research prototype and theoretical framework. It is not a diagnostic tool, not a replacement for clinical care, and must not be used as the basis for individual medical decisions.

---

## 1. System Overview and Organizing Principle

The VLEP Mainframe is a secure, versioned, evidence-ledger-based medical research platform.

The system is organized around two central outputs:

1. **Immutable Evidence Ledger (L)** — An append-only, cryptographically hashed, time-stamped store of atomic clinical observations that can never be overwritten.
2. **Current-State Epilepsy Profile (CSEP / P_snapshot)** — A versioned, recomputable snapshot of the patient's best-supported phenotype state, derived from the ledger under a specified nosological framework.

**Core Architectural Tuple:**
```
VLEP = (L, N, F, P_snapshot)
```
where:
- `L` = Immutable Evidence Ledger
- `N` = Nosological Framework (e.g., ILAE-2025)
- `F` = Resolution Function (algorithm version)
- `P_snapshot` = Current-State Epilepsy Profile at time t

**Phenotype Vector:**
```
P(t) = { S(t), E(t), C(t), B(t), M(t), R(t) }
```
- `S(t)` — Seizure type cluster
- `E(t)` — Etiology class
- `C(t)` — Syndrome classification
- `B(t)` — Biomarker vector (EEG, imaging, genetic)
- `M(t)` — Comorbidity burden
- `R(t)` — Treatment response state

**Trajectory Velocity:**
```
v(t) = dP/dt
```
Used to forecast SUDEP risk, treatment failure likelihood, and phenotype transition states.

**Raw evidence is never overwritten. Phenotype conclusions are versioned, recomputable, and traceable back to source evidence.**

---

## 2. Multi-Platform Surface Architecture

| Layer | Audience | Purpose |
|---|---|---|
| Public project website | General public, patients, researchers, clinicians | Explain project, display aggregate metrics, publish methodology, establish legitimacy |
| Research portal | Approved collaborators, internal team | View de-identified cohort dashboards, validation results, model performance |
| Clinical/reviewer portal | Clinicians, epileptologists, expert reviewers | Validate CSEP outputs, inspect evidence trails, approve/reject classifications |
| Patient/participant portal | Patients, caregivers, research participants | Seizure logs, medication history, triggers, consent, uploads |
| Backend pipeline system | System processes | Ingest, normalize, store evidence, compute phenotype states, run models |
| Governance/admin console | Project owner, data stewards, compliance reviewers | Audit logs, permissions, consent, versioning, model monitoring |
| API layer | External integrations | EHRs, FHIR, research tools, dashboards, analytics |

---

## 3. Public Medical Website Plan

### URL Structure
```
/                          Homepage
/about                     About the Framework
/methodology               Algorithm Methodology
/algorithm                 Mathematical Specification
/pipeline                  Six-Stage Pipeline Documentation
/dashboard                 Public Real-Time Metrics Dashboard
/research                  Research Portal Entry
/publications              White papers, posters, preprints
/documentation             Technical docs, data dictionary, API docs
/governance                Data governance, IRB readiness, ethics
/privacy                   Privacy policy, de-identification, consent
/contact                   Collaboration and contact intake
```

### Homepage Content
- Project title: **Versioned Longitudinal Epilepsy Phenotype System**
- One-sentence thesis: *A versioned, longitudinal architecture for representing epilepsy as an evolving phenotype rather than a static diagnosis.*
- Brief explanation of: evidence ledger, CSEP, nosological versioning, predictive modeling, research validation roadmap
- Research prototype / not a diagnostic tool disclaimer
- Visual architecture diagram
- Links to methodology, publications, dashboards, and governance

### Required Trust Elements

| Element | Purpose |
|---|---|
| Scientific advisory page | List reviewers/advisors |
| Methodology page | Transparent algorithm explanation |
| Validation status | State what has and has not been clinically validated |
| Model cards | Model purpose, inputs, limits, risks |
| Data dictionary | Define every major variable |
| Governance policy | Review, correction, versioning process |
| Privacy policy | PHI, de-identification, retention |
| Consent policy | Participant rights |
| Security page | Encryption, access control, audit logs |
| Publication page | Papers, posters, preprints, technical specs |
| Changelog | Algorithm and taxonomy updates |
| Medical disclaimer | Not emergency or diagnostic care |

### Public Dashboard Metrics

| Category | Example Metrics |
|---|---|
| System activity | Total de-identified records, evidence events, CSEP recomputations |
| Data completeness | % records with seizure type, EEG, medications, etiology, comorbidity |
| Phenotype distribution | Focal / generalized / unknown / unclassified proportions |
| Etiology distribution | Genetic / structural / infectious / metabolic / immune / traumatic / unknown |
| Treatment response | Drug-responsive / emerging resistance / pharmacoresistant distribution |
| Model performance | AUC, sensitivity, specificity, calibration, false-positive rates |
| Data quality | Missingness rate, contradiction flags, validation queue size |
| Versioning | Current classification framework version, last recomputation date |
| Research progress | Retrospective cohort size, prospective enrollment, validation milestones |

**Privacy rules:** Suppress small-count cells. Do not expose rare combinations, exact timestamps, raw notes, genetic variants, or individual-level trajectories publicly.

---

## 4. Six-Stage Backend Pipeline

### Stage 1 — Data Collection and Source Intake

**Purpose:** Collect all source material contributing to the phenotype ledger.

**Inputs:** EHR records, neurology notes, seizure diaries, medication lists, EEG reports, MRI/CT/PET/SPECT, genetic testing, lab reports, hospitalizations, neuropsychology reports, comorbidity assessments, trigger reports, uploads, wearable data.

**Required Services:**

| Service | Function |
|---|---|
| Upload service | PDFs, images, structured files, audio/video, CSVs |
| FHIR connector | Future EHR integration |
| Manual entry forms | Structured clinical/research entry |
| Patient diary API | Seizure and trigger reporting |
| Document parser | Text extraction from reports |
| Source registry | Provenance and source metadata |

**Design Rule:** All incoming data is stored first as raw source evidence, before interpretation.

---

### Stage 2 — Normalization, De-Identification, and CDE Mapping

**Purpose:** Convert raw data into standardized clinical data elements aligned with ILAE classifications, NINDS epilepsy CDEs, medication ontologies, and comorbidity instruments.

**Processing Tasks:**
- Extract structured fields and normalize medical terminology
- Map to ILAE seizure classification, epilepsy type, syndrome framework, etiology category, NINDS CDEs, medication ontology, diagnostic procedure categories, comorbidity instruments
- Identify date ranges and observation timestamps
- Detect missingness and contradictions
- Assign source confidence scores
- De-identify research copies

**Required Services:**

| Service | Function |
|---|---|
| NLP extraction service | Extracts seizure descriptions, medications, findings |
| Terminology service | Maps to controlled vocabularies |
| CDE mapper | Aligns fields with epilepsy data elements |
| De-identification service | Removes PHI for research/public analytics |
| Quality validator | Checks plausibility and completeness |

---

### Stage 3 — Immutable Evidence Ledger

**Purpose:** Commit normalized observations into a time-stamped, source-attributed, cryptographically hashed append-only ledger.

**Ledger Definition:**
```
L = { (t_i, D_i, s_i, a_i, v_i) }
```
where: t_i = observation time, D_i = data element, s_i = source attribution, a_i = audit metadata, v_i = classification version.

**Ledger Entry Structure:**
```json
{
  "ledger_event_id": "uuid",
  "patient_or_subject_id": "pseudonymous-id",
  "observation_timestamp": "2026-06-21T00:00:00Z",
  "data_element": {
    "domain": "seizure_semiology",
    "value": "focal impaired awareness seizure",
    "raw_text": "...",
    "coded_terms": []
  },
  "source": {
    "type": "clinician_note",
    "document_id": "uuid",
    "author_or_origin": "neurology_report",
    "source_date": "..."
  },
  "audit_metadata": {
    "certainty": 0.82,
    "validation_status": "unreviewed",
    "extraction_method": "nlp_v1.3",
    "reviewer_id": null
  },
  "classification_version": {
    "nosology_version": "ILAE-2025",
    "algorithm_version": "VLEP-0.1.0"
  },
  "hash": "cryptographic-hash",
  "previous_hash": "previous-ledger-hash"
}
```

**Key Rule:** Nothing in the ledger is overwritten. Corrections are new events, not edits.

---

### Stage 4 — Phenotype Assertion and CSEP Computation

**Purpose:** Convert ledger evidence into structured phenotype assertions and current-state profile snapshots.

**CSEP Computation:**
```
P_snapshot(t_now) = F(L, N_current, θ)
```

**CSEP Output Domains:**

| Domain | Output |
|---|---|
| Seizure type | Focal/generalized/unknown/unclassified; subtype probabilities |
| Epilepsy type | Focal/generalized/combined/unknown |
| Syndrome | Classification with version and confidence |
| Etiology | Genetic/structural/infectious/metabolic/immune/traumatic/post-surgical/unknown |
| Biomarkers | EEG, HFOs, spike rate, spectral features, imaging findings |
| Treatment response | Drug-responsive/emerging resistance/pharmacoresistant |
| Comorbidity burden | Psychiatric/cognitive/behavioral/developmental/sleep/medical |
| Risk factors | SUDEP, injury, status epilepticus, nocturnal seizure risk |
| Confidence vector | Certainty by domain |
| Evidence links | Supporting ledger events |
| Review status | Unreviewed/clinician-reviewed/validated/rejected |

**Phenotype Assertion Schema:**
```json
{
  "assertion_id": "uuid",
  "subject_id": "pseudonymous-id",
  "assertion_type": "treatment_response",
  "value": "emerging_resistance",
  "confidence": 0.74,
  "effective_start": "2026-03-01",
  "supporting_ledger_events": ["event-1", "event-2", "event-3"],
  "contradicting_ledger_events": ["event-4"],
  "algorithm_version": "VLEP-0.1.0",
  "nosology_version": "ILAE-2025",
  "review_status": "pending_expert_review"
}
```

---

### Stage 5 — Predictive Modeling, Forecasting, and Validation

**Purpose:** Use structured longitudinal phenotype data for research-grade predictive outputs.

**Model Families:**

| Model | Purpose |
|---|---|
| DRE risk model | Estimate probability of drug-resistant epilepsy |
| Seizure frequency model | Forecast seizure burden over defined intervals |
| SUDEP risk factor model | Track known risk factor burden |
| ASM response model | Estimate medication response patterns |
| Comorbidity trajectory model | Track psychiatric/cognitive evolution |
| Biomarker model | Evaluate EEG/imaging contribution |
| Surgical candidacy model | Research-stage decision support screening |

**DRE Risk Model (Logistic Regression):**
```
DRE_probability = sigmoid(
  β0
  + β1(first_ASM_response)
  + β2(log_baseline_seizure_frequency)
  + β3(MRI_lesion_present)
  + β4(developmental_encephalopathy_indicator)
  + β5(cognitive_impairment)
  + β6(time_since_diagnosis)
)
```

**Validation Metrics:** AUC, sensitivity, specificity, precision, recall, calibration, missingness, expert agreement, false positive/negative rates, subgroup performance, temporal drift.

**Evidence Survival Rate:** The heuristic grading system filters over 1,140 literature relations down to 239 Tier 1 gold-standard claims (17.6% evidence survival rate) to prevent AI hallucinations and maintain scientific rigor.

---

### Stage 6 — Output Generation, Review, Publication, and Monitoring

**Purpose:** Generate human-readable and controlled machine-readable outputs with a mandatory expert review workflow.

**Output Types:**

| Output | Audience |
|---|---|
| CSEP clinical summary | Clinicians/reviewers |
| Patient-friendly profile | Patients/caregivers |
| Research phenotype export | Approved researchers |
| Public aggregate dashboard | Public website |
| Validation reports | Internal/research team |
| Model cards | Public/research transparency |
| Audit reports | Governance/compliance |
| API responses | Software integrations |

**Review Workflow:**
```
Pipeline output generated
        ↓
Evidence links attached
        ↓
Confidence score assigned
        ↓
Contradictions flagged
        ↓
Reviewer queue
        ↓
Clinician/research validation
        ↓
Approved output → current CSEP version
        ↓
Aggregate metrics update public/research dashboards
```

**Monitoring:** Pipeline failure rate, extraction accuracy, data drift, model drift, reviewer disagreement, classification version changes, security events, consent status changes.

---

## 5. Core Software Architecture

### Architecture Style: Modular Service-Oriented

```
Frontend apps (Public / Patient / Reviewer / Research / Admin)
   ↓
API Gateway
   ↓
Authentication / Authorization (MFA, RBAC)
   ↓
Domain Services
   ↓
Pipeline Orchestration (Prefect / Dagster)
   ↓
Databases / Object Storage / Model Registry
   ↓
Analytics and Dashboard Layer
```

### Core Services

| Service | Responsibility |
|---|---|
| Identity service | Users, roles, authentication, MFA |
| Consent service | Participant consent, withdrawal, data-use permissions |
| Data ingestion service | File uploads, EHR imports, forms, APIs |
| Document processing service | OCR, NLP, metadata extraction |
| CDE normalization service | Maps data to standardized fields |
| Evidence ledger service | Immutable event storage |
| Phenotype assertion service | Converts evidence to structured claims |
| CSEP computation service | Generates current-state epilepsy profile |
| Nosology version service | Stores classification framework versions |
| Algorithm engine | Deterministic and statistical phenotype logic |
| Model service | ML inference and validation |
| Review service | Clinician/reviewer validation workflows |
| Reporting service | PDFs, dashboards, exports |
| Public metrics service | Safe aggregate statistics |
| Audit service | Logs all user/system actions |
| De-identification service | Creates research/public-safe datasets |
| Notification service | Alerts reviewers/admins |
| API gateway | External integrations |

---

## 6. Data Architecture

### Main Databases

| Database | Purpose |
|---|---|
| Operational relational DB (PostgreSQL) | Users, projects, forms, permissions, CSEP metadata |
| Append-only event store | Immutable evidence ledger |
| Document/object storage (S3-compatible) | PDFs, EEG files, images, reports, uploads |
| Search index (OpenSearch) | Search across notes, reports, evidence |
| Analytics warehouse (ClickHouse / Postgres) | Aggregate metrics and research dashboards |
| Feature store | Model-ready features |
| Model registry (MLflow) | Model versions, metrics, approvals |
| Audit log store | Security, access, reviewer actions |
| Terminology/ontology store | ILAE terms, CDEs, medications, syndromes |

### Core Data Objects
```
Subject
ConsentRecord
SourceDocument
EvidenceLedgerEvent
PhenotypeAssertion
CurrentStateEpilepsyProfile
NosologyVersion
AlgorithmVersion
ModelVersion
RiskScore
SeizureEvent
MedicationTrial
DiagnosticFinding
ComorbidityAssessment
ReviewerDecision
PublicMetric
AuditEvent
```

---

## 7. Portal Specifications

### A. Research Portal
**URL prefix:** `/research/`
**Modules:** cohorts, phenotype-distribution, model-performance, data-quality, exports, publication-workbench

### B. Clinical Reviewer Portal
**URL prefix:** `/reviewer/`
**Modules:** cases, csep, evidence-ledger, conflicts, validation-queue, audit-trail

### C. Patient / Participant Portal
**URL prefix:** `/patient/`
**Modules:** consent, seizure-log, triggers, medications, symptoms, uploads, reports

### D. Admin and Governance Console
**URL prefix:** `/admin/`
**Modules:** users, roles, data-sources, pipeline-runs, model-registry, nosology-versions, audit, privacy, public-dashboard-controls

---

## 8. Algorithm Module Architecture

| Module | Function |
|---|---|
| Seizure classification module | Maps evidence to seizure type cluster |
| Etiology module | Assigns genetic/structural/infectious/metabolic/immune/traumatic/unknown |
| Syndrome module | Applies age-versioned syndrome definitions |
| Biomarker module | Processes EEG/imaging/genetic markers |
| Treatment-response module | Classifies responsive/emerging resistance/pharmacoresistant |
| Comorbidity module | Computes psychiatric/cognitive/behavioral burden |
| Risk module | Computes DRE/SUDEP/adverse-event risk scores |
| Confidence module | Certainty from data density, recency, consistency, source quality |
| Conflict module | Flags contradictory evidence |
| Versioning module | Recomputes outputs when nosology or algorithm version changes |

---

## 9. Technology Stack

### Frontend
| Use | Stack |
|---|---|
| Public website | Next.js / React |
| Dashboards | Next.js + Recharts or Plotly |
| Patient portal | React / Next.js |
| Reviewer portal | React / Next.js |
| Admin console | React Admin or custom Next.js |

### Backend
| Use | Stack |
|---|---|
| API | FastAPI (Python) or NestJS |
| Pipeline orchestration | Prefect or Dagster |
| Primary database | PostgreSQL |
| Event ledger | PostgreSQL append-only tables |
| Object storage | S3-compatible (MinIO / AWS S3) |
| Search | OpenSearch / Elasticsearch |
| Analytics warehouse | ClickHouse or PostgreSQL initially |
| ML service | Python, scikit-learn, PyTorch |
| Model registry | MLflow |
| Authentication | Auth0, Clerk, or Keycloak |
| Monitoring | Grafana + Prometheus + OpenTelemetry |
| Audit logs | Immutable PostgreSQL table + object archive |

### Standards
- HL7 FHIR R4 and USCDI v3
- HL7 v2 feeds
- CDS Hooks for active alerts
- OIDC/OAuth 2.0 security
- ILAE seizure and epilepsy classifications
- NINDS Epilepsy Common Data Elements
- ICD-10 / ICD-11 compatibility
- DSM-5 / psychiatric instrument mappings
- OMOP CDM (future research scaling)

---

## 10. Security, Privacy, and Compliance

### Security Controls
- Encryption at rest and in transit
- Role-based access control (RBAC)
- Multi-factor authentication (MFA)
- Separate public/private infrastructure
- Immutable audit logs
- Least-privilege access
- Secure file upload scanning
- Secrets management
- Database backups and disaster recovery
- Environment separation: development / staging / production / research sandbox

### Privacy Controls
- Pseudonymous subject IDs
- De-identification pipeline
- Consent-linked data use
- Right-to-withdraw handling
- Aggregate-only public metrics
- Research export approval workflow
- Sensitive field masking
- Reviewer access logging

### Compliance Readiness
- HIPAA-style safeguards
- IRB review readiness
- Informed consent
- Data-use agreements
- Clinical validation documentation
- Audit logs for publication reproducibility

---

## 11. Minimum Viable Product Roadmap

### Phase 0 — Foundation
- Public website with static methodology pages
- Architecture documentation
- Data dictionary draft
- Governance and disclaimer pages
- Manual demo dashboard with synthetic aggregate metrics only
- **No sensitive patient data accepted**

### Phase 1 — Research Prototype
- Secure login, file upload, manual data entry
- Evidence ledger and basic CDE mapping
- CSEP generator and algorithm version tracking
- Reviewer queue and aggregate research dashboard
- Synthetic or fully de-identified records only

### Phase 2 — Retrospective Validation
- Batch import pipeline and de-identification pipeline
- Expert review workflow
- Validation metrics dashboard and model performance reports
- Target: 500–1,000 de-identified patient records
- Exportable research dataset

### Phase 3 — Prospective Multi-Center Pilot
- Patient portal, EHR integration
- Real-time clinical entry and live CSEP recomputation
- Secure clinician dashboard and model monitoring
- IRB/compliance workflows
- Target: 2,000–5,000 patients, live clinical environment

### Phase 4 — Longitudinal Outcome Study
- Long-term cohort tracking and outcome forecasting
- Longitudinal trajectory visualization
- Publication workbench and research collaboration APIs
- Advanced model comparison tools
- Target: 5–10 year follow-up validation

---

## 12. Build Order

1. **Define the canonical data model** — Subject, EvidenceLedgerEvent, PhenotypeAssertion, CSEP, NosologyVersion, AlgorithmVersion, ReviewerDecision, PublicMetric
2. **Build the evidence ledger first** — The ledger is the system's foundation; do not start with dashboards
3. **Build the CSEP generator** — Implement deterministic v0.1 logic before machine learning
4. **Build the reviewer portal** — Human validation must exist before making serious phenotype claims
5. **Build the public site and aggregate dashboards** — Publish aggregate non-sensitive metrics only
6. **Add interpretable predictive models** — Logistic regression DRE risk, Poisson seizure burden, rule-based SUDEP risk, confidence scoring
7. **Add advanced ML as isolated research modules** — Deep learning and EEG seizure detection (CNN/VGGNet/ResNet) are biomarker subsystems, not core validated phenotype engine components

---

## 13. System Architecture Diagram

```
                      PUBLIC WEBSITE
      ------------------------------------------------
      About | Methodology | Dashboard | Publications
      Governance | Documentation | Collaboration
                         |
                         v
                  Public Metrics API
                         |
      ------------------------------------------------
      Aggregate / De-identified Metrics Database
      ------------------------------------------------
                      SECURE PLATFORM
      ------------------------------------------------
      Patient Portal | Reviewer Portal | Research Portal
      Admin Console | API Gateway
      ------------------------------------------------
                         |
                         v
                  Auth + Consent Layer
                         |
                         v
                 Data Intake Services
      ------------------------------------------------
      Uploads | Forms | EHR/FHIR | Diaries | Reports
      ------------------------------------------------
                         |
                         v
            Normalization + CDE Mapping Layer
      ------------------------------------------------
      NLP | Terminology | De-ID | Quality Checks
      ------------------------------------------------
                         |
                         v
                Immutable Evidence Ledger
      ------------------------------------------------
      Timestamp | Data Element | Source | Audit | Version
      ------------------------------------------------
                         |
                         v
              Phenotype Assertion Engine
      ------------------------------------------------
      Seizure | Etiology | Syndrome | Biomarker
      Treatment | Comorbidity | Risk | Confidence
      ------------------------------------------------
                         |
                         v
                  CSEP Generator
      ------------------------------------------------
      Current-State Epilepsy Profile + Evidence Links
      ------------------------------------------------
                         |
                         v
             Review, Validation, and Monitoring
      ------------------------------------------------
      Expert Review | Conflict Flags | Model Metrics
      Versioning | Audit Logs | Governance
      ------------------------------------------------
```

---

## 14. Related Source Documents

- `docs/source-documents/SOURCE_REGISTRY.md` — Full source document catalog
- `algorithm/` — Algorithm module specifications
- `docs/` — Technical documentation
- `publications/` — Academic and research publications
- `research/` — Research notebooks and analysis
- Source infographic: `The_VLEP_Precision_Neurology_Algorithm.jpeg`
- Source mind map: `NotebookLM-Mind-Map.jpeg`
- Source presentation: `LPA_Technical_Blueprint.pptx`

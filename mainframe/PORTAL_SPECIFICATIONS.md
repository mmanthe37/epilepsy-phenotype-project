# VLEP Portal Specifications
## Detailed Portal Design for Each System Surface

**Version:** 0.1.0  
**Date:** 2026-06-21  

---

## Public Website Portal

**Audience:** General public, patients, researchers, clinicians, institutions.

### Pages

| Path | Content |
|---|---|
| `/` | Homepage: thesis, system overview, architecture diagram, disclaimers, navigation |
| `/about` | The Epilepsy Phenotyping Problem; Why Static Registries Are Insufficient; What Is a Versioned Longitudinal Epilepsy Phenotype; Evidence Ledger vs. CSEP; Nosological Versioning; Validation Status |
| `/methodology` | Mathematical framework, input domains, output domains, plain-language explanations |
| `/algorithm` | VLEP = (L, N, F, P_snapshot) formal specification; P(t) vector; v(t) trajectory velocity |
| `/pipeline` | Six-stage pipeline documentation |
| `/dashboard` | Public aggregate metrics dashboard (de-identified, suppression rules enforced) |
| `/research` | Research portal entry (requires authentication) |
| `/publications` | White paper, formal spec, validation protocol, poster, data dictionary, API docs, changelog, model cards |
| `/documentation` | Architecture docs, technical specs, CDE documentation |
| `/governance` | Governance policy, review process, versioning, IRB readiness |
| `/privacy` | Privacy policy, PHI handling, de-identification, retention, consent |
| `/contact` | Collaboration intake, institutional contact |

### Patient and Public Education Section

- What epilepsy phenotyping means
- What seizure types are
- Why seizure logs matter
- What EEG/MRI/genetics contribute
- What treatment response means
- What drug-resistant epilepsy means
- How patient-reported data may support research
- Privacy and consent explanation

### Safety and Medical Disclaimers

- Not a medical diagnosis tool
- Not a replacement for a neurologist or epileptologist
- Predictions are research outputs unless clinically validated
- Emergency guidance directs users to emergency services
- Sensitive data must not be submitted outside the secure portal
- All research use requires appropriate consent, de-identification, and governance

---

## Secure Research Portal

**Audience:** Approved collaborators, reviewers, internal research team.  
**Authentication:** Required. Role: RESEARCHER or above.

| Module | Path | Function |
|---|---|---|
| Cohorts | `/research/cohorts` | View de-identified cohort definitions and demographics |
| Phenotype Distribution | `/research/phenotype-distribution` | Aggregate phenotype vectors across cohort |
| Model Performance | `/research/model-performance` | AUC, sensitivity, specificity, calibration charts |
| Data Quality | `/research/data-quality` | Missingness rates, contradiction flags, completeness |
| Exports | `/research/exports` | Approved aggregate dataset downloads |
| Publication Workbench | `/research/publication-workbench` | Collaborative manuscript and analysis tools |

---

## Clinical Reviewer Portal

**Audience:** Clinicians, epileptologists, expert reviewers, internal validators.  
**Authentication:** Required. Role: REVIEWER or CLINICIAN.

| Module | Path | Function |
|---|---|---|
| Cases | `/reviewer/cases` | Queue of cases awaiting review |
| CSEP | `/reviewer/csep` | Current-State Epilepsy Profile viewer |
| Evidence Ledger | `/reviewer/evidence-ledger` | Inspect individual ledger events and lineage |
| Conflicts | `/reviewer/conflicts` | Review contradictory evidence pairs |
| Validation Queue | `/reviewer/validation-queue` | Approve, reject, or request additional evidence |
| Audit Trail | `/reviewer/audit-trail` | Full action log for all reviewer decisions |

**Key requirement:** Every phenotype profile modification must be traced to supporting evidence. No assertion may be approved without at least one linked ledger event.

---

## Patient / Participant Portal

**Audience:** Patients, caregivers, research participants.  
**Authentication:** Required. Role: PARTICIPANT.

| Module | Path | Function |
|---|---|---|
| Consent | `/patient/consent` | View, sign, withdraw consent; data-use permissions |
| Seizure Log | `/patient/seizure-log` | Structured seizure diary with date, type, duration, postictal state |
| Triggers | `/patient/triggers` | Report precipitants: sleep deprivation, stress, alcohol, hormonal, missed medication, other |
| Medications | `/patient/medications` | Current ASMs, doses, start/stop dates, adherence |
| Symptoms | `/patient/symptoms` | Side effects, comorbidity symptoms, PRO instruments |
| Uploads | `/patient/uploads` | Secure medical record, EEG report, imaging report uploads |
| Reports | `/patient/reports` | Plain-language summaries (if permitted by study protocol) |

---

## Admin and Governance Console

**Audience:** Project owner, data stewards, security admins, compliance reviewers.  
**Authentication:** Required. Role: ADMIN or GOVERNANCE.

| Module | Path | Function |
|---|---|---|
| Users | `/admin/users` | Create, manage, suspend user accounts |
| Roles | `/admin/roles` | Assign and modify role-based permissions |
| Data Sources | `/admin/data-sources` | Register and monitor data source provenance |
| Pipeline Runs | `/admin/pipeline-runs` | View pipeline execution logs and failure alerts |
| Model Registry | `/admin/model-registry` | Track model versions, approval status, performance history |
| Nosology Versions | `/admin/nosology-versions` | Manage ILAE/classification framework version catalog |
| Audit | `/admin/audit` | Full system audit log viewer |
| Privacy | `/admin/privacy` | De-identification settings, retention schedules, data-use agreements |
| Public Dashboard Controls | `/admin/public-dashboard-controls` | Approve and publish aggregate metrics to public dashboard |

---

## API Layer

**Audience:** External EHR systems, FHIR endpoints, research tool integrations, analytics services.

### Standards
- HL7 FHIR R4 for clinical data exchange
- USCDI v3 data elements
- CDS Hooks for alert integration
- OIDC / OAuth 2.0 for authentication
- REST + JSON as primary interface
- Versioned API endpoints (e.g., `/api/v1/...`)

### Key Endpoints (Phase 2+)
- `POST /api/v1/evidence` — Submit new evidence event
- `GET /api/v1/csep/{subject_id}` — Retrieve current CSEP snapshot
- `GET /api/v1/phenotype-history/{subject_id}` — Retrieve version history
- `GET /api/v1/public-metrics` — Public aggregate dashboard data
- `POST /api/v1/fhir/Patient` — FHIR Patient resource ingestion
- `POST /api/v1/fhir/Observation` — FHIR Observation ingestion

# Formal Algorithmic Specification for a Versioned Longitudinal Epilepsy Phenotype System

**Document Type:** Formal Technical Specification  
**Project:** Epilepsy Phenotype Project  
**Version:** 2.0 (Finalized)  
**Domain:** Computational Phenotyping, Mathematical Modeling, Distributed Data Engineering

---

## 1. Introduction and Objectives

The Versioned Longitudinal Epilepsy Phenotype (VLEP) system and Longitudinal Phenotyping Algorithm (LPA) together define an algorithmic framework for representing epilepsy as a dynamic, time-evolving disease state rather than a static diagnostic label. The core objective is to transform heterogeneous clinical, biomarker, and literature-derived evidence into a versioned, longitudinal phenotype representation suitable for clinical reasoning, predictive modeling, and research interoperability.

The algorithmic specification formalizes:
1. The data model for an immutable evidence ledger and derived Current-State Epilepsy Profile (CSEP)
2. Feature engineering and prior-weighting mechanisms that integrate structured EHR data with literature-based evidence confidence weights
3. The longitudinal modeling stack (GLMM, HMM, survival ensembles) that infers latent disease states and time-to-event hazards
4. Versioning mechanisms that decouple historical observations from evolving nosological frameworks
5. The algorithm operates as a layered system with clear separation between data ingestion, evidence storage, phenotypic inference, and versioned profile outputs

At a high level, the system can be represented as the tuple:

$$\text{VLEP} = (\mathcal{L}, \mathcal{N}_k, \Phi, \text{CSEP}(t))$$

where $\mathcal{L}$ is the immutable evidence ledger, $\mathcal{N}_k$ is the current nosological framework version, $\Phi$ is the phenotype resolution function, and $\text{CSEP}(t)$ is the current-state epilepsy profile at a given time.

---

## 2. System Overview and Components

### 2.1 High-Level Architecture

The VLEP system consists of four primary layers:

1. **Data Ingestion Layer** — Ingests timestamped, multi-source clinical trajectories from EHR systems (HL7 FHIR R4, openEHR), EEG/neuroimaging platforms, genetic testing results, and patient-reported outcomes
2. **Evidence Storage Layer** — The immutable evidence ledger $\mathcal{L}$ stores all observations with cryptographic provenance, uncertainty quantification, and source quality metadata
3. **Phenotypic Inference Layer** — The LPA maps evidence to latent disease states via GLMM, HMM, and survival ensemble models
4. **Versioned Profile Output Layer** — Generates the CSEP snapshot using the current nosological framework $\mathcal{N}_k$, decoupled from historical raw observations

### 2.2 Immutable Evidence Ledger $\mathcal{L}$

All clinical observations are stored as append-only, cryptographically hashed records. Each ledger entry $\ell_j$ contains:
- Timestamp $t_j \in \mathbb{R}^+$
- Observation vector $\mathbf{x}_j \in \mathbb{R}^D$
- Source quality metadata $(\text{tier}, \text{confidence}, \text{provenance\_hash})$
- Framework version tag $k$ active at time of ingestion
- Uncertainty interval $[\mathbf{x}_j^{\text{low}}, \mathbf{x}_j^{\text{high}}]$

The ledger is immutable: observations are never modified or deleted. Corrections are appended as new entries with a `supersedes` reference pointer.

---

## 3. Formal Definitions — $P(t)$ and $T_p$

### 3.1 Patient Trajectory

Let the patient cohort be $\mathcal{C} = \{p_1, p_2, \dots, p_N\}$. For each patient $p \in \mathcal{C}$, the longitudinal observation trajectory is:

$$T_p = \{ (t_0, \mathbf{x}(t_0)), (t_1, \mathbf{x}(t_1)), \dots, (t_K, \mathbf{x}(t_K)) \}$$

where $t_k \in \mathbb{R}^+$ is the continuous temporal coordinate and $\mathbf{x}(t_k) \in \mathbb{R}^D$ is the $D$-dimensional sparse feature vector at encounter $k$.

### 3.2 Dynamic Phenotype Vector

The state of patient $j$ at time $t$ is:

$$P_j(t) = \sum_{i=1}^{n} w_i \cdot x_{ij}(t) \cdot \delta_i(t - t_{\text{event}})$$

where:
- $w_i$ = literature-derived evidentiary weight for feature $i$ (from heuristic provenance tiers)
- $x_{ij}(t)$ = boolean or continuous value of feature $i$ for patient $j$ at time $t$
- $\delta_i(\Delta t)$ = feature-specific temporal decay function
  - Structural/genetic features: $\delta_i = 1$ (no decay)
  - Episodic features: $\delta_i(\Delta t) = e^{-\lambda_i \Delta t}$

### 3.3 Evidentiary Weight Function

The weight $w_i$ for claim $i$ is calculated as:

$$w_i = \alpha S_{\text{design}} + \beta S_{\text{stat}} + \gamma S_{\text{cite}} + \lambda S_N$$

where:
- $S_{\text{design}}$ = hierarchical study design score (RCT/meta-analysis = 1.0; prospective cohort = 0.8; retrospective = 0.5; case report = 0.2)
- $S_{\text{stat}}$ = inverse weighting of reported $p$-value and confidence interval width
- $S_{\text{cite}}$ = citation PageRank score from network analysis
- $S_N$ = logarithmic scaling of cohort size
- Coefficients $\alpha, \beta, \gamma, \lambda$ tuned via grid search against a 1,000-claim gold-standard annotation set

---

## 4. Longitudinal Modeling Stack

### 4.1 Baseline Trajectory: Generalized Linear Mixed-Effects Models (GLMM)

For seizure frequency modeling, let $Y_{ij}(t)$ denote the seizure count for patient $j$ in time window $t$ to $t + \Delta t$:

$$\log(E[Y_{ij}(t)]) = \mathbf{x}_{ij}(t)^\top \boldsymbol{\beta} + b_{ij}$$

where $\boldsymbol{\beta}$ are fixed-effect coefficients and $b_{ij} \sim \mathcal{N}(0, \sigma^2_b)$ are patient-specific random intercepts capturing baseline heterogeneity.

### 4.2 Latent State Transitions: Hidden Markov Model (HMM)

Disease state transitions are modeled as a continuous-observation HMM with hidden states $\mathbf{S} = \{s_1, s_2, \dots, s_M\}$ representing latent phenotypic phases (e.g., drug-responsive, drug-tolerant, pharmacoresistant, SUDEP-risk):

$$P(s_{t+1} | s_t) = \mathbf{A}_{s_t, s_{t+1}}$$

$$P(\mathbf{x}(t) | s_t) = \mathcal{N}(\boldsymbol{\mu}_{s_t}, \boldsymbol{\Sigma}_{s_t})$$

Viterbi decoding identifies the most probable disease state sequence $s^*_{1:T} = \arg\max P(s_{1:T} | \mathbf{x}_{1:T})$.

### 4.3 Survival Modeling: Gradient Boosting Survival Ensembles

Time-to-event outcomes (pharmacoresistance onset, SUDEP risk) are modeled non-parametrically:

$$h(t | \mathbf{x}) = h_0(t) \cdot \exp(f(\mathbf{x}))$$

where $f(\mathbf{x})$ is estimated by a gradient boosting ensemble. Right-censoring is handled via Inverse Probability of Censoring Weighting (IPCW).

### 4.4 Temporal Sparsity Imputation

For missing observations between encounters, Gaussian Process imputation with sparse inducing points is applied:

$$P(\mathbf{x}(t^*) | \mathbf{X}_{\text{obs}}, \mathbf{t}_{\text{obs}}) = \mathcal{GP}(\mu^*(t^*), k^*(t^*, t^*))$$

---

## 5. Heuristic Provenance Tier Specification

| Tier | Cohort Size | p-value | Study Design | Confidence Modifier |
|------|-------------|---------|--------------|--------------------|
| **Tier 1** | $N \ge 200$ | $p \le 0.01$ | Prospective, MR, LDSC | +0.25 (size) +0.12 (RCT) |
| **Tier 2** | $N \ge 50$ | $p \le 0.05$ | Retrospective, case-control | Base weight |
| **Tier 3** | $N \ge 20$ | Any | Observational, case series | Downweighted; cross-validation required |

Tier 1 claims act as deterministic anchor points. Tier 2 claims require cross-validation when conflicting with Tier 1. Tier 3 claims are flagged as exploratory and excluded from primary phenotype inference unless no higher-tier evidence exists.

---

## 6. Versioning Mechanism

The VLEP system decouples raw observations (immutable ledger $\mathcal{L}$) from the nosological framework $\mathcal{N}_k$ used for phenotype interpretation. When ILAE, OMIM, or other authoritative classifications update:

1. The new framework version $\mathcal{N}_{k+1}$ is registered with a timestamp and changelog
2. Historical ledger entries remain unchanged
3. The phenotype resolution function $\Phi(\mathcal{L}, \mathcal{N}_{k+1})$ re-derives the CSEP under the updated framework
4. Both the prior CSEP (under $\mathcal{N}_k$) and updated CSEP (under $\mathcal{N}_{k+1}$) are stored for longitudinal comparability

This versioning architecture ensures that historical clinical observations are never retroactively distorted by classification updates.

---

## 7. Validation Metrics

| Metric | Target | Achieved (Retrospective) |
|--------|--------|-------------------------|
| Tier 1 extraction concordance | > 90% | **94.5%** |
| Overall pipeline concordance | > 80% | **85%** |
| EHR retrospective diagnostic concordance | > 88% | **91%** (N=15,000) |
| Predictive lead time (pharmacoresistance) | > 2 months | **4.2 months** |
| td-AUROC (time-dependent, IPCW-adjusted) | > 0.80 | Target for Phase 2 |
| Harrell's C-index | > 0.75 | Target for Phase 2 |

---

## 8. Data Standards and Interoperability

- **EHR Integration:** HL7 FHIR R4, SMART on FHIR application layer, openEHR archetypes
- **Ontologies:** SNOMED-CT (clinical findings), RxNorm (medications), HPO (phenotypes), LOINC (labs/EEG), HGNC (genes), FMA (neuroanatomy)
- **Common Data Model:** OMOP CDM for cross-institutional harmonization
- **NLP Architecture:** Fine-tuned BioClinicalBERT / Bio-LinkBERT on neurological corpora
- **Graph Database:** Neo4j for knowledge representation of claim-phenotype relationships
- **Privacy:** HIPAA-eligible cloud compute (AWS/Azure), cryptographic ledger hashing, federated learning architecture for multi-site deployments

---

## 9. Deployment Phases

| Phase | Timeline | Scope | Key Milestone |
|-------|----------|-------|---------------|
| Phase 0 | Months 1–3 | Foundation | Pipeline lock, IRB approval, infrastructure provision |
| Phase 1 | Months 4–9 | Pilot/Validation | Retrospective validation (N=10,000 EHR records), shadow deployment |
| Phase 2 | Months 10–15 | Clinical Integration | SMART on FHIR UI, 10-clinician soft launch, NPS > 40 |
| Phase 3 | Months 16–24 | Scale & Adoption | Enterprise rollout (150+ providers), active CDS, federated learning |

---

## 10. References and Source Documents

This specification synthesizes the following project documents:
- `publications/journal-article/vlep-journal-article.md` — Peer-review manuscript
- `algorithm/longitudinal-phenotyping-algorithm.md` — LPA technical paper
- `publications/formal-spec/epilepsy-categorization-state.md` — ILAE limitations review
- `research/experimental-theory-proposal.md` — NIH-style grant proposal
- `research/roadmap-implementation-plan.md` — Clinical adoption roadmap
- `research/official-publication.md` — Comprehensive project publication
- `research/summary-analysis.md` — Executive summary and pipeline methodology

*Full bibliography in `research/bibliography.md`. Key citations: Scheffer et al. 2017 (ILAE Classification), Fisher et al. 2017 (ILAE Epilepsy Definition), Berkovic et al. GGE GWAS, Marini et al. SCN1A cohort, NINDS CDE Epilepsy Protocol v2.*

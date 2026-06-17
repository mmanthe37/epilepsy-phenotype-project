# Experimental Theory Proposal: An Evidence-Driven Longitudinal Phenotyping Framework for Epilepsy Trajectory Prediction

## Project Summary

Epilepsy is a complex neurological disorder characterized by recurrent, unprovoked seizures and heterogeneous treatment responses. Despite the availability of over thirty anti-seizure medications (ASMs), approximately 30–40% of patients develop drug-resistant epilepsy, resulting in significant morbidity and mortality. Current clinical phenotyping paradigms rely on static, categorical classifications (e.g., the ILAE framework) that fail to capture the dynamic, non-linear progression of the disease. Furthermore, the volume of biomedical literature describing novel phenotypic associations, genetic markers, and neuroimaging indicators exceeds the cognitive capacity of practicing clinicians, leaving critical prognostic data locked within unstructured text.

This project proposes the development and validation of an evidence-driven, computational longitudinal phenotyping framework. The core objective is to construct a time-varying phenotype vector, $P(t)$, parametrized by continuous extraction and heuristic weighting of claims derived from biomedical literature. By applying NLP models to unstructured scientific text, we extract phenotype-defining associations and map them to standard ontologies (HPO, RxNorm). These claims are scored for evidentiary provenance to generate weight parameters $w_i$.

The clinical application of $P(t)$ will be evaluated in two phases. Phase 1 involves a retrospective cohort ($N \ge 200$) of deeply phenotyped patients from EHR to calibrate vector weights and train predictive algorithms (LSTM networks and XGBoost). Phase 2 is a prospective, multi-center observational trial ($N \ge 500$) to validate the framework's capacity to predict 12-month and 24-month seizure trajectories and ASM refractoriness.

## Specific Aims

**Aim 1: Extract, formalize, and heuristically weight phenotype-defining claims from heterogeneous biomedical literature.**

- **Aim 1A — Ontological Mapping and Relation Extraction:** Deploy fine-tuned transformer models (PubMedBERT, Bio-LinkBERT) to extract tripartite entity relations (Subject-Predicate-Object) linking genotypic, EEG, and neuroimaging markers to pharmacological outcomes. Map extracted entities to OMOP Common Data Model vocabularies.

- **Aim 1B — Evidentiary Provenance Scoring:** Develop a deterministic heuristic algorithm to assign a continuous confidence weight ($w_i$) to each claim. The weighting function incorporates study design, sample size, journal citation metrics, temporal decay of publication, and replication density across independent studies.

**Aim 2: Construct and calibrate a dynamic algorithmic longitudinal phenotype vector $P(t)$ using a retrospective EHR cohort ($N \ge 200$).**

- **Aim 2A — EHR Harmonization and Vector Initialization:** Abstract longitudinal clinical data spanning ≥ 36 months from $N \ge 200$ patients. The phenotype vector $P(t)$ is formalized as the dot product of literature-derived weights $w_i$, patient-specific feature matrices $x_i(t)$, and temporal decay $\delta(t)$.

- **Aim 2B — Algorithm Training and Weight Optimization:** Apply Bayesian updating to calibrate literature-derived priors $w_i$ based on observed retrospective outcomes. Train LSTM networks to forecast time-to-refractoriness and 6-month seizure freedom probabilities, optimizing for cross-entropy loss.

**Aim 3: Prospectively validate individualized seizure trajectory predictions in a multi-center cohort ($N \ge 500$).**

- **Aim 3A — Prospective Multi-Center Cohort:** Recruit $N \ge 500$ newly diagnosed or newly refractory patients across a minimum of three comprehensive epilepsy centers. Collect standardized EEG data, genomic panels, and structured ASM titration logs prospectively.

- **Aim 3B — Primary Outcome Validation:** Primary outcomes: 12-month and 24-month seizure freedom status; time-to-pharmacoresistance. Validate using time-dependent AUROC (td-AUROC, IPCW-adjusted) and Harrell's C-index.

## Dynamic Phenotype Vector Formalization

The state of patient $j$ at time $t$ is:

$$P_j(t) = \sum_{i=1}^{n} w_i \cdot x_{ij}(t) \cdot \delta_i(t - t_{\text{event}})$$

where:
- $w_i = \alpha S_{\text{design}} + \beta S_{\text{stat}} + \gamma S_{\text{cite}} + \lambda S_N$ (normalized linear combination, coefficients tuned via grid search against 1,000-claim gold-standard annotation set)
- $S_{\text{design}}$: Meta-analyses/RCT = 1.0; prospective cohort = 0.8; retrospective = 0.5; case report = 0.2
- $\delta_i(\Delta t) = e^{-\lambda_i \Delta t}$ for episodic features; $\delta_i = 1$ for structural/genetic features

## Statistical Analysis Plan

- **Longitudinal seizure frequency:** Generalized Linear Mixed Models (GLMM) with random patient intercepts
- **Latent state transitions:** Continuous-observation Hidden Markov Models (HMM), Viterbi decoding
- **Time-to-event:** Extended Cox proportional hazards with time-dependent covariates; Gradient Boosting Survival Ensembles for non-parametric estimation
- **Imputation:** Gaussian Process (GP) imputation with sparse inducing points for irregular temporal spacing
- **Validation:** IPCW-adjusted td-AUROC, Harrell's C-index, Brier Score

## Budget Overview

| Category | Allocation |
|----------|------------|
| Personnel (data scientists, epileptologists, NLP engineers) | $1,200,000 |
| Cloud infrastructure (HIPAA-eligible AWS/Azure) | $285,000 |
| Multi-center data agreements & IRB coordination | $150,000 |
| EHR integration development (FHIR/SMART) | $250,000 |
| Validation & publication costs | $150,000 |
| **Total** | **$2,035,000** |

## Timeline

| Phase | Duration | Primary Deliverable |
|-------|----------|--------------------|
| Phase 0: Foundation | Months 1–3 | Pipeline lock, IRB approval, infrastructure |
| Phase 1: Pilot/Validation | Months 4–9 | Retrospective EHR validation, shadow deployment |
| Phase 2: Clinical Integration | Months 10–15 | SMART on FHIR UI, soft launch, NPS > 40 |
| Phase 3: Scale | Months 16–24 | Enterprise rollout, federated learning, active CDS |

---
*Cross-reference: `publications/formal-spec/formal-algorithmic-specification.md`, `algorithm/longitudinal-phenotyping-algorithm.md`*

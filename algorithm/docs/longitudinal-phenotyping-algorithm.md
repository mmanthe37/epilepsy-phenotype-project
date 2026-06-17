# Technical Paper: The Longitudinal Phenotyping Algorithm (LPA)

**Project:** Epilepsy Phenotype Project  
**Domain:** Computational Phenotyping, Mathematical Modeling, Distributed Data Engineering  
**Version:** 2.0 (Finalized)

---

## Abstract

This paper details the formal computational, mathematical, and data engineering architecture of the Longitudinal Phenotyping Algorithm (LPA). The primary objective is to extract phenotype-defining clinical claims from unstructured biomedical literature and map them to a high-dimensional, longitudinally sampled EHR vector space.

The mathematical core relies on three integrated methodologies:
1. **GLMMs** — patient-specific baseline trajectory adjustments
2. **Continuous-observation HMMs** — latent disease state decoding
3. **Gradient Boosting Survival Ensembles** — non-parametric time-to-event hazard estimation

Temporal sparsity is addressed through parametric exponential decay and scalable Gaussian Process (GP) imputation. Validation uses IPCW td-AUROC and Harrell's Concordance Index.

---

## 1. Formal Definitions: P(t) and T_p

### 1.1 Patient Trajectory

Let cohort $\mathcal{C} = \{p_1, \dots, p_N\}$. For each patient $p$:

$$T_p = \{ (t_0, \mathbf{x}(t_0)), (t_1, \mathbf{x}(t_1)), \dots, (t_K, \mathbf{x}(t_K)) \}$$

where $t_k \in \mathbb{R}^+$ is the temporal coordinate and $\mathbf{x}(t_k) \in \mathbb{R}^D$ is the $D$-dimensional clinical feature vector.

### 1.2 Phenotypic State Distribution

$$P(t) = \Pr(\mathbf{Z}(t) \mid \mathcal{F}_t, \mathbf{W})$$

- $\mathbf{Z}(t) \in \mathcal{S}$: latent phenotypic state (e.g., Well-Controlled, Refractory, Status Risk)
- $\mathcal{F}_t = \sigma(\{\mathbf{x}(\tau) : \tau \le t\})$: natural filtration — ensures look-ahead-free predictions
- $\mathbf{W} = \text{diag}(\omega_1, \dots, \omega_D)$: diagonal prior matrix from heuristic evidence confidence

Optimal trajectory: $\hat{T}^* = \arg\max \Pr(\mathbf{Z}(t_0), \dots, \mathbf{Z}(t_K) \mid \mathcal{F}_{t_K}, \mathbf{W})$

---

## 2. Data Ingestion & Feature Engineering

### 2.1 Lambda Architecture
- **Batch (Apache Spark):** OMOP CDM → Parquet
- **Stream (Apache Kafka):** HL7 FHIR R4 → real-time $P(t)$ updates

### 2.2 Hyperbolic Graph Embeddings

Ontology graph $G = (V, E)$ embedded via Poincaré embeddings $\psi: V \rightarrow \mathbb{R}^d$, preserving hierarchical semantic similarity. Raw observation $\mathbf{x}(t_k)$ → dense embedded matrix $\mathbf{E}(t_k) \in \mathbb{R}^{|\mathbf{x}| \times d}$.

### 2.3 30-Day Window Aggregation

$$\bar{\mathbf{x}}_j = \bigoplus_{t_k \in w_j} \phi(\mathbf{E}(t_k))$$

$\phi(\cdot)$ = TF-IDF normalization adapted for clinical vocabulary; $\bigoplus$ = max/average pooling.

### 2.4 Heuristic Evidence Weighting

$$\tilde{\mathbf{x}}_j = \mathbf{W} \bar{\mathbf{x}}_j$$

Complexity: $\mathcal{O}(D)$ per window. Amplifies phenotype-defining features ($\omega_i \to 1$); dampens administrative codes ($\omega_i \to 0$).

---

## 3. Modeling Stack

### 3.1 GLMM — Baseline Separation

$$\mathbf{y}(t) = \mathbf{X}(t)\boldsymbol{\beta} + \mathbf{Z}(t)\mathbf{u} + \boldsymbol{\epsilon}(t)$$

$\mathbf{u} \sim \mathcal{N}(\mathbf{0}, \mathbf{G})$; $\boldsymbol{\epsilon}(t) \sim \mathcal{N}(\mathbf{0}, \mathbf{R})$. Variance components estimated via REML (Newton-Raphson).

### 3.2 HMM — Latent State Decoding

$$a_{ij} = \Pr(Z_{t+1} = S_j \mid Z_t = S_i)$$

$$b_j(\tilde{\mathbf{x}}_t) = \sum_{c=1}^{C} c_{jc} \mathcal{N}(\tilde{\mathbf{x}}_t \mid \boldsymbol{\mu}_{jc}, \boldsymbol{\Sigma}_{jc})$$

Parameters learned via Baum-Welch (EM). Optimal path decoded via Viterbi: $\mathcal{O}(K \cdot M^2)$.

### 3.3 Gradient Boosting Survival Ensembles

$$h(t \mid \tilde{\mathbf{x}}(t)) = \lim_{\Delta t \to 0} \frac{\Pr(t \le T_{\text{event}} < t + \Delta t \mid T_{\text{event}} \ge t))}{\Delta t}$$

Random Survival Forests; node splitting via log-rank statistic; cumulative hazard via Nelson-Aalen estimator. Bypasses Cox proportional hazards assumptions.

---

## 4. Temporal Smoothing & GP Imputation

### 4.1 Exponential Decay

$$\mathbf{x}_{\text{decayed}}(t_k, t) = \mathbf{x}(t_k) \odot e^{-\boldsymbol{\lambda}(t - t_k)}$$

- Structural/genetic features: $\lambda_i = 0$ (permanent)
- Episodic features: high $\lambda_i$ (rapid decay)

### 4.2 Gaussian Process Imputation

$$P(\mathbf{x}(t^*) \mid \mathbf{X}_{\text{obs}}) = \mathcal{GP}(\mu^*(t^*), k^*(t^*, t^*))$$

Matérn $\nu = 3/2$ kernel. Sparse inducing points: $\mathcal{O}(NM^2)$ where $M \ll N$.

---

## 5. Validation Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| td-AUROC | $\Pr(\hat{P}_i(t) > \hat{P}_j(t) \mid T_i \le t < T_j)$ | > 0.80 |
| Harrell's C | $\sum I(\hat{T}_i < \hat{T}_j)I(T_i < T_j)\Delta_i / \sum I(T_i < T_j)\Delta_i$ | > 0.75 |
| Brier Score | $\frac{1}{N}\sum \hat{W}_i(t)(\hat{P}_i(t) - Y_i(t))^2$ | < 0.20 |

---

## 6. Technology Stack

| Layer | Technology |
|-------|------------|
| EHR | HL7 FHIR R4, SMART on FHIR, openEHR |
| Batch | Apache Spark, Parquet, OMOP CDM |
| Stream | Apache Kafka |
| Graph DB | Neo4j |
| NLP | BioClinicalBERT, Bio-LinkBERT, BioRoBERTa |
| Ontologies | SNOMED-CT, RxNorm, HPO, LOINC, HGNC, FMA |
| Privacy | HIPAA Safe Harbor, cryptographic hashing, federated learning |

---

*Cross-reference: `publications/formal-spec/formal-algorithmic-specification.md`, `publications/journal-article/vlep-journal-article.md`*

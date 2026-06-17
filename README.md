# Epilepsy Phenotype Project — Monohub

> **Versioned Longitudinal Epilepsy Phenotype (VLEP) System** | Longitudinal Phenotyping Algorithm (LPA) | Current-State Epilepsy Profile (CSEP)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Status: Research](https://img.shields.io/badge/Status-Research-orange)]()

---

## Overview

This repository is the comprehensive monohub for the **Epilepsy Phenotype Project** — a rigorous, evidence-driven research initiative to design, formalize, and implement a versioned longitudinal framework for characterizing, tracking, and predicting the evolution of epilepsy phenotypes across the clinical lifespan.

The central output of this project is the **Longitudinal Phenotyping Algorithm (LPA)**, which ingests heterogeneous clinical, electrophysiological, genetic, and neuroimaging evidence over time to maintain an immutable provenance ledger and compute a dynamic, versioned phenotype profile — the **Current-State Epilepsy Profile (CSEP)**.

---

## Table of Contents

- [Project Background](#project-background)
- [Core Components](#core-components)
- [Repository Structure](#repository-structure)
- [Algorithm Overview](#algorithm-overview)
- [Mathematical Formalism](#mathematical-formalism)
- [Getting Started](#getting-started)
- [Documentation](#documentation)
- [Publications & Research](#publications--research)
- [Data & References](#data--references)
- [Contributing](#contributing)
- [License](#license)

---

## Project Background

Epilepsy is a chronic neurological disorder affecting ~70 million people globally. Despite increasingly sophisticated classification frameworks (ILAE 2017/2022/2025), clinical data infrastructure remains fragmented — static registries, point-in-time diagnoses, and siloed records fail to capture the multidimensional, longitudinally evolving nature of epilepsy phenotypes.

**The core problem:** No standardized system exists to:
1. Track phenotypic state vectors across time with versioned, provenance-anchored records
2. Integrate multisource evidence (EHR, EEG, genetics, imaging, patient-reported outcomes) into a unified computational representation
3. Apply validated statistical models to predict phenotype transitions, pharmacoresistance emergence, and adverse outcomes
4. Maintain alignment with evolving ILAE nosological frameworks

**The VLEP solution** introduces:
- An **immutable evidence ledger** recording all observations with temporal and provenance metadata
- A **phenotype state vector** P(t) capturing six longitudinal dimensions
- A **longitudinal phenotyping algorithm** integrating NLP extraction, heuristic tiering, Bayesian models, and survival analysis
- A **CSEP resolver** generating interpretable, clinician-facing phenotype profiles

---

## Core Components

| Component | Description |
|---|---|
| **LPA Engine** | Core algorithm orchestrating evidence ingestion, phenotype update, and CSEP resolution |
| **Evidence Ledger** | Immutable append-only ledger `L = {(tᵢ, Dᵢ, sᵢ, aᵢ, vᵢ)}ⁿ` |
| **Phenotype Vector** | P(t) = {S(t), E(t), C(t), B(t), M(t), R(t)} — six-dimensional state |
| **NLP Pipeline** | Extracts 239 phenotype-defining claims from unstructured clinical text |
| **Provenance Tiering** | Heuristic confidence weighting (Tier 1=1.0, Tier 2=0.6, Tier 3=0.2) |
| **GLMM Model** | Generalized linear mixed model for longitudinal outcomes |
| **HMM Model** | Hidden Markov Model for latent phenotype state transitions |
| **Survival Ensemble** | Gradient-boosted survival analysis for time-to-event prediction |
| **GP Imputation** | Sparse Gaussian Process for missing temporal data |
| **CSEP Resolver** | Synthesizes evidence into clinician-interpretable current-state profile |
| **Ontology Embeddings** | Graph-based embeddings over ILAE/HPO ontological hierarchy |
| **Validation Suite** | td-AUROC, C-index, Brier score metrics |

---

## Repository Structure

```
epilepsy-phenotype-project/
│
├── algorithm/                    # Core algorithm software & engine
│   ├── core/
│   │   ├── lpa_engine.py        # Main LPA orchestration engine
│   │   ├── evidence_ledger.py   # Immutable evidence ledger
│   │   ├── phenotype_vector.py  # P(t) state vector definition
│   │   └── csep_resolver.py     # CSEP profile resolver
│   ├── models/
│   │   ├── glmm.py              # Generalized linear mixed model
│   │   ├── hmm.py               # Hidden Markov Model (Baum-Welch/Viterbi)
│   │   ├── survival_ensemble.py # Gradient boosting survival model
│   │   └── dre_risk_model.py    # Drug-resistant epilepsy risk model
│   ├── features/
│   │   ├── temporal_decay.py    # Exponential decay δ(t,tₖ;γ)
│   │   ├── evidence_weighting.py# Heuristic confidence tiers
│   │   ├── ontology_embeddings.py # Graph embeddings (ILAE/HPO)
│   │   └── temporal_aggregation.py
│   ├── pipeline/
│   │   ├── ingestion.py         # FHIR/EHR data ingestion layer
│   │   ├── nlp_extraction.py    # NLP claim extraction (239 phenotype claims)
│   │   ├── provenance_tiering.py# Source-tier classification engine
│   │   └── gp_imputation.py     # Gaussian Process imputation
│   ├── versioning/
│   │   └── nosological_framework.py # ILAE versioning framework
│   └── validation/
│       └── metrics.py           # td-AUROC, C-index, Brier score
│
├── docs/                         # All documentation
│   ├── framework/
│   │   ├── vlep-framework.md    # VLEP system framework
│   │   ├── lpa-algorithm.md     # LPA technical documentation
│   │   └── csep-profile.md      # CSEP specification
│   ├── protocol/
│   │   ├── study-protocol.md    # Full study protocol
│   │   └── data-governance.md   # Data standards & governance
│   ├── publications/            # Formatted publications
│   ├── implementation/
│   │   └── roadmap.md          # Implementation roadmap
│   └── references/
│       └── bibliography.md     # Full reference list
│
├── publications/                 # Research outputs & drafts
│   ├── formal-spec/             # Formal Algorithmic Specification
│   ├── journal-article/         # Academic journal article
│   ├── technical-paper/         # LPA technical paper
│   └── drafts/                  # Working drafts
│
├── data/                         # Data schemas, examples, evidence
│   ├── schema/                  # JSON schemas
│   ├── claims/                  # Phenotype claim definitions
│   ├── examples/                # Sample patient trajectories
│   └── ontologies/              # ILAE/HPO ontology references
│
├── research/                     # Research materials & evidence corpus
│   ├── literature/              # Key literature references
│   ├── evidence-corpus/         # Curated evidence base
│   └── validation/              # Validation study results
│
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
│
├── notebooks/                    # Jupyter notebooks
│   └── trajectory_simulation.ipynb
│
├── tools/                        # Utility scripts and reports
│   └── scripts/
│
├── requirements.txt
├── setup.py
├── CONTRIBUTING.md
└── LICENSE
```

---

## Algorithm Overview

The LPA operates in five sequential phases per clinical encounter:

1. **Ingestion** — Structured (FHIR/EHR) and unstructured (clinical notes) data are ingested and normalized
2. **NLP Extraction** — 239 phenotype-defining claims are extracted and classified from free text
3. **Provenance Tiering** — Each claim is assigned a confidence tier (T1–T3) based on source fidelity
4. **Evidence Ledger Update** — New observations are appended to the immutable ledger with temporal metadata
5. **CSEP Resolution** — Weighted, temporally decayed evidence is aggregated to compute the current-state profile

---

## Mathematical Formalism

### Phenotype State Vector

```
P(t) = {S(t), E(t), C(t), B(t), M(t), R(t)}
```
Where:
- **S(t)** — seizure type cluster (focal onset ± awareness impairment, generalized, unknown)
- **E(t)** — etiology class (genetic, structural, infectious, metabolic, immune, traumatic, unknown)
- **C(t)** — syndromic classification under current ILAE framework (age-versioned)
- **B(t)** — validated biomarker vector (EEG features, HFOs, imaging findings)
- **M(t)** — comorbidity burden (psychiatric, cognitive, behavioral)
- **R(t)** — treatment response state (drug-responsive, emerging resistance, pharmacoresistant)

### Evidence Ledger

```
L = {(tᵢ, Dᵢ, sᵢ, aᵢ, vᵢ)}ⁿᵢ₌₁
```
Where: tᵢ = timestamp, Dᵢ = data record, sᵢ = source identifier, aᵢ = author, vᵢ = ILAE version

### Temporal Decay

```
δ(t, tₖ; γ) = e^(−γ(t − tₖ))
```

### Confidence Weighting (Provenance Tiers)

| Tier | Source Type | Weight |
|------|-------------|--------|
| T1 | Specialist evaluation, clinical trial, genetically confirmed | w = 1.0 |
| T2 | GP/NP documentation, pharmacy records, structured EHR | w = 0.6 |
| T3 | Patient-reported outcomes, informal records | w = 0.2 |

### CSEP Resolution

```
CSEP(t) = argmax_{P} Σᵢ w(cᵢ) · δ(t, tᵢ; γ) · P(Dᵢ | phenotype = P)
```

---

## Getting Started

```bash
# Clone
git clone https://github.com/mmanthe37/epilepsy-phenotype-project.git
cd epilepsy-phenotype-project

# Install dependencies
pip install -r requirements.txt

# Run a basic phenotype computation
python -m algorithm.core.lpa_engine --demo

# Run tests
pytest tests/
```

---

## Documentation

| Document | Description |
|---|---|
| [VLEP Framework](docs/framework/vlep-framework.md) | Theoretical foundations of the versioned phenotype system |
| [LPA Algorithm](docs/framework/lpa-algorithm.md) | Technical specification of the Longitudinal Phenotyping Algorithm |
| [CSEP Profile](docs/framework/csep-profile.md) | Current-State Epilepsy Profile specification |
| [Study Protocol](docs/protocol/study-protocol.md) | Full research study protocol |
| [Implementation Roadmap](docs/implementation/roadmap.md) | Clinical adoption roadmap |
| [Bibliography](docs/references/bibliography.md) | Complete reference list |

---

## Publications & Research

| Publication | Status |
|---|---|
| [Formal Algorithmic Specification](publications/formal-spec/) | Finalized |
| [VLEP Framework Paper](publications/journal-article/) | Finalized |
| [Academic Journal Article](publications/journal-article/) | Finalized |
| [LPA Technical Paper](publications/technical-paper/) | Finalized |
| [Working Drafts](publications/drafts/) | In Progress |

---

## Data & References

- `data/schema/` — JSON schemas for all data structures
- `data/claims/` — The 239 phenotype-defining claims taxonomy
- `data/examples/` — Sample patient trajectories
- `research/literature/` — Annotated bibliography of key literature
- `research/evidence-corpus/` — Curated evidence base supporting LPA design

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT License — see [LICENSE](LICENSE).

---

*Epilepsy Phenotype Project | VLEP System v1.0 | Research & Algorithm Software*

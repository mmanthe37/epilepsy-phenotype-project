# VLEP: Variable Longitudinal Epilepsy Phenotyping Framework

## Overview

The **Variable Longitudinal Epilepsy Phenotype (VLEP)** framework provides a
formal mathematical specification for capturing, representing, and computationally
resolving the dynamic nature of epilepsy as a syndrome over time.

Traditional epilepsy classification systems (e.g., ILAE 2017) provide static
taxonomies. VLEP extends this with a **temporal phenotype function** that
characterizes how a patient's epilepsy profile evolves across clinical encounters,
treatment changes, and disease milestones.

---

## Core Construct: The Phenotype Vector P(t)

At any time point *t*, the patient's epilepsy phenotype is represented as a
six-dimensional state vector:

```
P(t) = { S(t), E(t), C(t), B(t), M(t), R(t) }
```

| Dimension | Symbol | Description |
|-----------|--------|-------------|
| Seizure type profile | S(t) | Current seizure semiology classification |
| Etiology class | E(t) | Causal classification (structural/genetic/immune/metabolic/infectious/unknown) |
| Syndromic classification | C(t) | Best-fit ILAE syndrome match |
| Biomarker vector | B(t) | EEG, MRI, genetics, biofluid markers |
| Comorbidity profile | M(t) | Neurological, psychiatric, and medical comorbidities |
| Treatment response state | R(t) | Current ASM response (drug-naive → drug-responsive → DRE → post-surgical) |

---

## The Evidence Ledger L

All clinical observations are recorded in an **immutable, timestamped evidence ledger**:

```
L = { (t₁, D₁, s₁, a₁, v₁), ..., (tₙ, Dₙ, sₙ, aₙ, vₙ) }
```

Where each entry (tᵢ, Dᵢ, sᵢ, aᵢ, vᵢ) contains:
- **tᵢ** — timestamp of the observation
- **Dᵢ** — data record (claim, note, test result, prescription)
- **sᵢ** — source tier (T1/T2/T3)
- **aᵢ** — author/provenance identifier
- **vᵢ** — version of the nosological framework applied

The ledger is **append-only** and uses SHA-256 content hashing for integrity verification.

---

## Source Tier Provenance System

Evidence quality is stratified into three tiers:

| Tier | Description | Weight |
|------|-------------|--------|
| T1 — High-fidelity | EEG reports, MRI reads, genetic panels, specialist notes | 1.0 |
| T2 — Moderate | ED summaries, non-specialist physician notes, pharmacy records | 0.6 |
| T3 — Low | Patient self-reports, surveys, claims data | 0.2 |

---

## Temporal Decay Function δ(t, tₖ; γ)

Because clinical evidence ages, VLEP applies temporal decay to weight
recent observations more heavily:

```
δ(t, tₖ; γ) = e^(−γ(t − tₖ))
```

Domain-specific decay rates (γ):

| Evidence Domain | γ | Half-life |
|----------------|---|-----------|
| Seizure frequency | 0.693 | ~1 year |
| Treatment response | 0.347 | ~2 years |
| MRI lesion | 0.087 | ~8 years |
| Genetic status | 0.0 | Never decays |

---

## CSEP Resolution Formula

The **Current State Epilepsy Profile (CSEP)** is the maximum a posteriori
estimate of the patient's phenotype given all available evidence:

```
CSEP(t) = argmax_P  Σᵢ w(cᵢ) · δ(t, tᵢ; γ) · P(Dᵢ | phenotype = P)
```

Where:
- **w(cᵢ)** = tier weight of claim cᵢ (T1=1.0, T2=0.6, T3=0.2)
- **δ(t, tᵢ; γ)** = temporal decay factor
- **P(Dᵢ | phenotype = P)** = likelihood of observing data Dᵢ given phenotype P

---

## References

- Fisher et al. (2017). ILAE Official Report: A practical clinical definition of epilepsy. *Epilepsia*.
- Scheffer et al. (2017). ILAE classification of the epilepsies. *Epilepsia*.
- Perucca et al. (2023). The ILAE classification of seizures and the epilepsies. *Epilepsia*.

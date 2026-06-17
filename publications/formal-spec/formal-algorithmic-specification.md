# Formal Algorithmic Specification for a Versioned Longitudinal Epilepsy Phenotype

**Author:** Michael Manthe  
**Status:** Finalized  
**Year:** 2025

---

## Abstract

We present a formal algorithmic specification for the **Versioned Longitudinal
Epilepsy Phenotype (VLEP)** system — a computational framework that models
epilepsy as a dynamic, multi-dimensional phenotypic state evolving over time.
The framework integrates probabilistic evidence weighting, temporal decay functions,
Hidden Markov Models, and survival analysis into a unified Longitudinal Phenotyping
Algorithm (LPA) that produces structured, auditable phenotype profiles at any
point in a patient's disease course.

---

## 1. Introduction

Epilepsy is not a single disease but a heterogeneous syndrome encompassing
hundreds of distinct etiological subtypes, seizure classifications, and
treatment trajectories. Current ILAE classification frameworks provide
taxonomic anchors but do not formally model **phenotype evolution** —
the systematic change in a patient's epilepsy characteristics across time
in response to treatment, maturation, and disease progression.

This specification formalizes:
1. The phenotype state representation P(t)
2. The evidence ledger L as the foundational data structure
3. The CSEP resolution algorithm for real-time phenotype estimation
4. The predictive models for trajectory forecasting

---

## 2. Phenotype Vector Specification

### 2.1 State Space Definition

At any time *t ∈ ℝ⁺*, the epilepsy phenotype is fully characterized by:

```
P(t) = { S(t), E(t), C(t), B(t), M(t), R(t) }
```

Where:
- **S(t)** ∈ SeizureTypeSpace — current predominant seizure type
- **E(t)** ∈ EtiologySpace — etiological classification
- **C(t)** ∈ SyndromeSpace — syndromic classification (ILAE 2017 or later)
- **B(t)** ∈ ℝᵈ — biomarker vector (EEG features, MRI findings, biofluid markers)
- **M(t)** ∈ {0,1}ᵐ — comorbidity indicator vector
- **R(t)** ∈ TreatmentResponseSpace — current treatment response state

### 2.2 State Spaces

```
SeizureTypeSpace = {
    FOCAL_AWARE, FOCAL_IMPAIRED_AWARENESS,
    FOCAL_TO_BILATERAL_TC, ABSENCE,
    MYOCLONIC, TONIC_CLONIC, TONIC, ATONIC,
    SPASMS, UNKNOWN
}

EtiologySpace = {
    STRUCTURAL, GENETIC, INFECTIOUS,
    METABOLIC, IMMUNE, UNKNOWN
}

TreatmentResponseSpace = {
    DRUG_NAIVE, DRUG_RESPONSIVE,
    EMERGING_RESISTANCE, PHARMACORESISTANT,
    POST_SURGICAL_SEIZURE_FREE,
    POST_SURGICAL_PERSISTENT
}
```

---

## 3. Evidence Ledger

### 3.1 Ledger Definition

```
L = { (tᵢ, Dᵢ, sᵢ, aᵢ, vᵢ) }ⁿᵢ₌₁
```

- **tᵢ** — timestamp (UTC)
- **Dᵢ** — data record (DataRecordType ∈ {CLAIM, NOTE, LAB, IMAGING, GENETIC, RX, SURVEY})
- **sᵢ** — source tier ∈ {T1, T2, T3}
- **aᵢ** — author identifier
- **vᵢ** — nosological framework version (e.g., "ILAE_2017")

### 3.2 Immutability Constraint

The ledger is **append-only**. No entry may be modified or deleted.
Corrections are appended as new entries referencing the original entry ID.

### 3.3 Integrity Verification

Each entry carries a SHA-256 content hash:
```
h(entry) = SHA256(t || D || s || a || v)
```

The ledger integrity hash is computed as:
```
H(L) = SHA256(h(e₁) || h(e₂) || ... || h(eₙ))
```

---

## 4. Temporal Decay

### 4.1 Decay Function

```
δ(t, tₖ; γ) = exp(−γ · (t − tₖ))
```

### 4.2 Domain-Specific Decay Rates

| Evidence Domain | γ | Justification |
|----------------|---|---------------|
| Seizure frequency | ln(2) ≈ 0.693 | Clinical relevance halves ~annually |
| ASM response | 0.347 | Changes visible over 2-year timeframe |
| EEG findings | 0.231 | EEG stable unless new event |
| MRI lesion | 0.087 | Structural lesions persist years |
| Genetic status | 0.0 | Pathogenic variants do not change |

---

## 5. CSEP Resolution Algorithm

### 5.1 Formula

```
CSEP(t) = argmax_P  ∑ᵢ w(cᵢ) · δ(t, tᵢ; γ) · P(Dᵢ | phenotype = P)
```

### 5.2 Algorithm

```
Algorithm CSEP_RESOLVE(patient_id, t):
    L ← LEDGER.query(patient_id)
    For each dimension d in {S, E, C, R}:
        scores ← {}
        For each value v in STATE_SPACE(d):
            score ← 0
            For each entry eᵢ in L:
                if RELEVANT(eᵢ, d):
                    score += TIER_WEIGHT(eᵢ.tier) ·
                             DECAY(t, eᵢ.timestamp, γ_d) ·
                             LIKELIHOOD(eᵢ.data, d=v)
            scores[v] ← score
        P*(d) ← argmax_v scores[v]
    Return PhenotypeReport(P*(S), P*(E), P*(C), P*(R), confidence_scores)
```

---

## 6. Predictive Models

### 6.1 Hidden Markov Model

Five latent states encode disease phase:
1. Seizure-free (SF)
2. Drug-responsive (DR)
3. Emerging resistance (ER)
4. Pharmacoresistant (PR)
5. Post-surgical (PS)

Transitions governed by clinically-calibrated matrix A₅ₓ₅.
Decoding via Viterbi algorithm.

### 6.2 GLMM for Seizure Frequency

```
log(λₜ) = Xₜβ + Zₜu + εₜ
```

Where λₜ = expected seizure frequency at time t,
Xₜ = fixed effects (ASM dose, time since onset),
Zₜ = random effects (patient-specific trajectory).

### 6.3 Survival Analysis

Nelson-Aalen baseline hazard + gradient-boosted covariate adjustment
for DRE onset prediction. Output: probability of DRE by 24 months.

---

## 7. Implementation

Reference implementation: Python 3.9+  
Repository: `https://github.com/mmanthe37/epilepsy-phenotype-project`  
Entry point: `python -m algorithm.core.lpa_engine --demo`

---

## References

See `docs/references/bibliography.md` for full citation list.

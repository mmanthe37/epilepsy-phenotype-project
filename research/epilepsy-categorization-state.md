# The Current State of Epilepsy Categorization and Diagnosis: Moving Toward a Longitudinal, Evidence-Weighted Phenotypic Framework

## Executive Summary

Clinical epileptology relies on a diagnostic framework fundamentally unsuited for the neurobiology it attempts to describe. We classify a highly dynamic, lifelong network disorder using discrete, static taxonomic buckets. Despite the influx of high-resolution neuroimaging, continuous intracranial EEG, and whole-exome sequencing, the fundamental paradigm of epilepsy categorization remains rooted in a "snapshot-in-time" methodology. Clinicians gather complex, high-dimensional data, reduce it to unstructured text, and force it through rigid decision trees to assign a categorical syndromic label.

This reductionist approach creates immediate and compounding clinical failures. Traditional taxonomies fail to accommodate the continuous evolution of patient phenotypes driven by ontogeny, structural network progression, pharmacological interventions, and genetic heterogeneity. The clinical consequence is a diagnostic process fraught with diagnostic inertia, misclassification, and suboptimal patient outcomes. A patient assigned a diagnostic label at age five often retains that label at age fifteen, even if their underlying electroclinical network has radically rewired itself.

This paper critically reviews the current state of epilepsy categorization and diagnosis, detailing the severe structural limitations of existing clinical workflows. We advocate for a complete paradigm shift: the implementation of a computational framework utilizing longitudinal phenotype vectors, denoted as $P(t)$. In this model, diagnoses are not static labels but dynamic, high-dimensional vectors continuously updated based on probabilistic evidence claims.

## Historical Context: The Evolution and Limitations of ILAE Classifications

The effort to standardize epileptic seizure and syndrome classification has been spearheaded by the International League Against Epilepsy (ILAE). The foundational frameworks established in 1981 and 1989 were revolutionary: they categorized seizures based on anatomical onset (partial versus generalized) and presence or absence of altered awareness, providing a common language for cross-institutional clinical trial comparison.

However, these systems became increasingly inadequate as high-resolution MRI and the genomic revolution illuminated underlying etiologies. The 1989 classification routinely forced highly heterogeneous patients into homogenous bins, or relegated vast swaths of the patient population to the clinically useless category of "unclassifiable."

In 2017, the ILAE introduced a major revision operating on a sequential, multi-level diagnostic approach: Seizure Type (Focal, Generalized, Unknown) → Epilepsy Type → Epilepsy Syndrome. Crucially, this update emphasized concurrent consideration of etiology (structural, genetic, infectious, metabolic, immune, unknown) and comorbidities at every stage.

While the 2017 classification provides a vastly more nuanced nomenclature, it remains inherently constrained by its categorical, discrete nature. It forces patients into predefined taxonomic bins that fail to capture the fluid reality of epileptogenesis.

## The DEE Trajectory Problem

Developmental and epileptic encephalopathies (DEEs) illustrate the failure of static taxonomy most clearly. A patient's electroclinical phenotype may shift dramatically during early childhood:

1. **Ohtahara syndrome** (neonatal): suppression-burst EEG, tonic spasms
2. **West syndrome** (infancy): hypsarrhythmia, infantile spasms
3. **Lennox-Gastaut syndrome** (early childhood): slow spike-and-wave, multiple seizure types

The ILAE framework accommodates this evolution by requiring the clinician to discard one label and apply another — a series of disconnected state assignments rather than a continuous integrated trajectory. The system does not quantitatively measure phenotype severity or the probabilistic certainty of a diagnostic assignment. A diagnosis is either present or absent.

## The Monogenic vs. Complex Evidence Divide

The epilepsy literature historically bifurcates the disorder into monogenic and complex polygenic forms. Monogenic epilepsies display high penetrance but extreme phenotypic pleiotropy. A single *SCN2A* mutation can manifest as benign familial neonatal seizures or as a profound DEE with intractable spasms and severe intellectual disability.

Complex epilepsies (Genetic Generalized Epilepsy [GGE], Rolandic Epilepsy) involve thousands of common genetic variants with minuscule individual effect sizes, aggregated via Polygenic Risk Scores (PRS).

Literature extraction systems that apply uniform validation criteria across both domains fail systematically. Rare variant claims inherently suffer from small sample sizes (frequently $N < 50$), while polygenic architecture claims routinely leverage biobank-scale cohorts ($N > 100,000$). A structured extraction pipeline must recognize these epidemiological realities and apply heuristics capable of untangling this evidence divide.

## Proposed Framework: The $P(t)$ Paradigm

We propose transitioning from deterministic taxonomy to a dynamic, computationally tractable model based on a continuous phenotype vector $P(t)$. In this framework:

- Diagnoses are probabilistic vectors, not binary labels
- Evidence is heuristically weighted by study design, sample size, and causal inference methodology
- Phenotypic profiles are continuously updated as new clinical data and literature evidence accumulate
- Historical observations are preserved in an immutable ledger, decoupled from evolving nosological frameworks

This architecture offers a mathematically sound method for real-time diagnostic updating, precise risk stratification, and targeted predictive therapeutic management — the operational foundation of precision epileptology.

---
*See `publications/formal-spec/formal-algorithmic-specification.md` for full mathematical formalization.*

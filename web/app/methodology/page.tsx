import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "VLEP Methodology",
};

export default function MethodologyPage() {
  return (
    <article className="space-y-6">
      <header className="space-y-2">
        <h2 className="text-xl font-semibold tracking-tight">Methodology</h2>
        <p className="text-sm text-slate-300">
          High-level description of the VLEP architecture, evidence ledger, and longitudinal
          phenotyping algorithm (LPA).
        </p>
      </header>

      <section className="space-y-3 text-sm leading-relaxed text-slate-200">
        <p>
          The VLEP system replaces static diagnosis registries with a versioned, longitudinal phenotype
          architecture. All atomic clinical observations, diagnostic test results, biomarkers, and
          patient-reported outcomes are committed into an immutable evidence ledger \(L\) as
          time-stamped, source-attributed events.[cite:44][cite:19]
        </p>
        <p>
          From this ledger, a deterministic resolution function \(F\) computes a Current-State Epilepsy
          Profile \(P_{{"{"}}snapshot{"}"}\) under a specified nosological framework \(N\). The profile
          summarizes seizure type, etiology, syndrome, biomarkers, comorbidity burden, and treatment
          response, along with a confidence vector and explicit links back to supporting ledger
          events.[cite:44][cite:33]
        </p>
        <p>
          The Longitudinal Phenotyping Algorithm (LPA) treats \(P(t)\) as a stochastic process, using a
          triad of methods—generalized linear mixed-effects models, hidden Markov models, and survival
          ensembles—to infer latent state transitions and outcome risks while strictly respecting
          natural filtration \(\mathcal{{"{"}}F_t{"}"}\).[cite:42][cite:43]
        </p>
      </section>

      <section className="space-y-3 text-sm leading-relaxed text-slate-200">
        <h3 className="text-sm font-semibold text-slate-100">Evidence Grading and Priors</h3>
        <p>
          Literature-derived claims are processed by an NLP pipeline and graded into heuristic tiers
          based on study design, cohort size, statistical rigor, and replication density. Only Tier 1
          and Tier 2 claims are allowed to influence safety-critical priors; Tier 3 evidence is
          restricted to research views.[cite:19][cite:42]
        </p>
        <p>
          These weights are stored alongside ledger events and exposed to phenotype modules as
          configurable priors \(W\), ensuring that causal genomic epidemiology and well-powered
          cohorts are emphasized over small case series.[cite:19][cite:21]
        </p>
      </section>
    </article>
  );
}

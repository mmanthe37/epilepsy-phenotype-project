import Link from "next/link";

export default function HomePage() {
  return (
    <div className="space-y-10">
      <section className="space-y-3">
        <h2 className="text-xl font-semibold tracking-tight">Project Overview</h2>
        <p className="text-sm leading-relaxed text-slate-200">
          The Versioned Longitudinal Epilepsy Phenotype (VLEP) system is a research architecture that
          separates immutable clinical observations from versioned diagnostic interpretations. The core
          tuple \(VLEP = (L, N, F, P_{{"{"}}snapshot{"}"})\) defines an append-only evidence ledger
          \(L\), a nosological framework \(N\) such as ILAE-2025, a resolution function \(F\), and a
          recomputable current-state epilepsy profile \(P_{{"{"}}snapshot{"}"}\).[cite:44][cite:46]
        </p>
        <p className="text-sm leading-relaxed text-slate-200">
          In this framework, a patient&apos;s state at time t is represented as a multi-domain phenotype
          vector \(P(t) = {{"{"}} S(t), E(t), C(t), B(t), M(t), R(t) {{"}"}}\), capturing seizure type,
          etiology, syndrome, biomarkers, comorbidity burden, and treatment response.[cite:44][cite:23]
          These representations are designed for research, predictive modeling, and future precision
          neurology applications, not for direct bedside diagnosis.
        </p>
      </section>

      <section className="grid gap-6 md:grid-cols-2">
        <Card
          title="Methodology"
          description="Learn how the immutable evidence ledger, longitudinal phenotyping algorithm, and risk models interact."
          href="/methodology"
        />
        <Card
          title="Governance &amp; Safety"
          description="Review HIPAA-style safeguards, immutability guarantees, and multi-tiered governance structures."
          href="/governance"
        />
      </section>

      <section className="space-y-2 text-xs text-slate-300">
        <h3 className="font-semibold tracking-tight">Clinical Use Disclaimer</h3>
        <p>
          The Epilepsy Phenotype Project and VLEP mainframe are currently research concepts and
          prototype implementations. They have not undergone regulatory clearance or prospective
          clinical validation. Any descriptions of clinical decision support, risk scores, or
          trajectory prediction are theoretical and must be treated as research only.[cite:44][cite:40]
        </p>
      </section>
    </div>
  );
}

function Card({
  title,
  description,
  href,
}: {
  title: string;
  description: string;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="block rounded-lg border border-slate-800 bg-slate-900/40 p-4 transition hover:border-sky-500/70 hover:bg-slate-900"
    >
      <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
      <p className="mt-1 text-xs leading-relaxed text-slate-300">{description}</p>
    </Link>
  );
}

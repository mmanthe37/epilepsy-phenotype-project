import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Governance & Safety",
};

export default function GovernancePage() {
  return (
    <article className="space-y-6">
      <header className="space-y-2">
        <h2 className="text-xl font-semibold tracking-tight">Governance &amp; Safety</h2>
        <p className="text-sm text-slate-300">
          Overview of HIPAA-style safeguards, immutable ledger guarantees, and the multi-tiered
          governance model.
        </p>
      </header>

      <section className="space-y-3 text-sm leading-relaxed text-slate-200">
        <p>
          The Epilepsy Phenotype Project is designed as a research platform with HIPAA-style technical
          and administrative safeguards. All PHI is encrypted in transit and at rest, access is
          governed by role-based access control with multi-factor authentication, and all ledger reads
          and writes are captured in immutable audit logs.[cite:44][cite:46]
        </p>
        <p>
          Data entering the system must pass through a registered source connector, normalization
          pipeline, and de-identification layer before it is committed as an `EvidenceLedgerEvent`.
          Corrections are represented as new events that reference earlier ones; historical data are
          never overwritten.[cite:44][cite:47]
        </p>
      </section>

      <section className="space-y-3 text-sm leading-relaxed text-slate-200">
        <h3 className="text-sm font-semibold text-slate-100">Governance Triad</h3>
        <p>
          Oversight is shared across an Executive Steering Committee (ESC), an Operational &amp;
          Technical Board (OTB), and a Clinical Advisory &amp; Ethics Group (CAEG). The ESC manages
          strategic alignment and capital expenditure, the OTB is responsible for integration
          stability, NLP tuning, and model monitoring, and the CAEG supervises clinical validity,
          alert fatigue, and equity audits.[cite:40]
        </p>
        <p>
          New ingestion rules or predictive models must first run in shadow deployment against
          retrospective or live streams, with predefined precision and recall thresholds, before any
          clinician-facing activation. This staged rollout is essential to avoid unsafe automation and
          to maintain clinician trust.[cite:40][cite:42]
        </p>
      </section>

      <section className="space-y-2 text-xs text-slate-300">
        <h3 className="font-semibold tracking-tight">Non-Clinical Status</h3>
        <p>
          This project has not undergone regulatory clearance or formal clinical validation. All
          descriptions of CDS hooks, SMART on FHIR integration, or risk scoring are part of a
          prospective roadmap and should be treated strictly as research design, not as an operational
          clinical system.[cite:40][cite:46]
        </p>
      </section>
    </article>
  );
}

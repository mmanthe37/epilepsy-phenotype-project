import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Versioned Longitudinal Epilepsy Phenotype System",
  description:
    "Research prototype public site for the Versioned Longitudinal Epilepsy Phenotype (VLEP) system.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased">
        <div className="mx-auto max-w-5xl px-4 py-10">
          <header className="mb-10 border-b border-slate-800 pb-6">
            <h1 className="text-2xl font-semibold tracking-tight">
              Versioned Longitudinal Epilepsy Phenotype System
            </h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-300">
              A research prototype for representing epilepsy as a dynamic, longitudinal, multi-domain
              phenotype rather than a static diagnostic label.
            </p>
          </header>
          <main>{children}</main>
          <footer className="mt-12 border-t border-slate-800 pt-6 text-xs text-slate-400">
            <p>
              This site describes a theoretical research framework and computational architecture. It is
              not a diagnostic tool and must not be used to guide individual patient care.
            </p>
          </footer>
        </div>
      </body>
    </html>
  );
}

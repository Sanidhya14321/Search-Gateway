import { PageGuide } from "@/components/common/page-guide";
import { PublicFooter } from "@/components/layout/public-footer";
import { PublicNav } from "@/components/layout/public-nav";

const FEATURES = [
  ["Entity Resolution", "Canonical identity matching before retrieval."],
  ["Hybrid Retrieval", "Vector + keyword retrieval merged by ranker."],
  ["Citation Formatting", "Structured evidence attached to claims and people."],
  ["Signal Tracking", "Hiring/funding/leadership signals across saved accounts."],
  ["Agent Workflows", "Lead finder, account brief, enrichment, research, ops debug."],
  ["Batch Enrichment", "CSV-like lead ingestion with write-back and confidence flags."],
];

export default function FeaturesPage() {
  return (
    <div className="page-wrap">
      <PublicNav />
      <main className="page-container space-y-6">
        <PageGuide
          title="Feature Map"
          description="This page describes what each platform capability does and when to use it in a production sales/research workflow."
          howToUse={[
            "Scan feature cards to choose the right workflow for your task.",
            "Pair Search + Signals for account monitoring.",
            "Use Agent + Enrichment when you need output at scale.",
          ]}
        />

        <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map(([title, text]) => (
            <article key={title} className="glass rounded-2xl p-4">
              <h2 className="font-display text-xl text-stone-900">{title}</h2>
              <p className="mt-2 text-sm text-stone-700">{text}</p>
            </article>
          ))}
        </section>
      </main>
      <PublicFooter />
    </div>
  );
}

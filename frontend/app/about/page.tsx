import { PublicFooter } from "@/components/layout/public-footer";
import { PublicNav } from "@/components/layout/public-nav";
import { PageGuide } from "@/components/common/page-guide";

export default function AboutPage() {
  return (
    <div className="page-wrap">
      <PublicNav />
      <main className="page-container space-y-6">
        <PageGuide
          title="About CRMind"
          description="This page explains the platform intent, architecture stance, and the type of operational teams that benefit most."
          howToUse={[
            "Read the mission statement to understand why entity-first retrieval matters.",
            "Review the operating principles before evaluating output quality.",
            "Use this as onboarding material for interview panels and managers.",
          ]}
        />

        <section className="grid gap-4 md:grid-cols-2">
          <article className="glass rounded-2xl p-5">
            <h2 className="font-display text-2xl text-stone-900">Mission</h2>
            <p className="mt-2 text-sm text-stone-700">
              Provide CRM intelligence that is inspectable, reproducible, and safe for decision-making.
              CRMind rejects memory-only generation and prioritizes source-linked evidence.
            </p>
          </article>
          <article className="glass rounded-2xl p-5">
            <h2 className="font-display text-2xl text-stone-900">Who it serves</h2>
            <p className="mt-2 text-sm text-stone-700">
              Interviewers, technical leads, revops managers, and account teams that need high-signal summaries,
              role-aware people discovery, and clearly traceable sourcing.
            </p>
          </article>
        </section>
      </main>
      <PublicFooter />
    </div>
  );
}

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { HeroVisuals } from "@/components/marketing/hero-visuals";
import { PublicFooter } from "@/components/layout/public-footer";
import { PublicNav } from "@/components/layout/public-nav";

const SUGGESTIONS = [
  "Find engineers at Stripe",
  "Account brief for Notion",
  "Hiring signals at Vercel",
];

export default function HomePage() {
  const router = useRouter();
  const [query, setQuery] = useState(SUGGESTIONS[0]);

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    router.push(`/search?q=${encodeURIComponent(query)}`);
  }

  return (
    <div className="page-wrap">
      <PublicNav />
      <main className="page-container space-y-8">
        <section className="hero-grid">
          <div className="glass rounded-3xl p-6 md:p-8">
            <p className="inline-flex rounded-full border border-teal-200 bg-teal-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-teal-800">
              Built For Interviewers, Tech Leads, And Managers
            </p>
            <h1 className="mt-4 font-display text-4xl leading-tight text-stone-900 md:text-6xl">
              CRM intelligence you can defend in a technical review.
            </h1>
            <p className="mt-4 max-w-2xl text-base text-stone-700 md:text-lg">
              CRMind is an entity-first search and enrichment system. It resolves organizations to canonical records,
              ranks evidence by relevance, freshness, and trust, and returns structured outputs with citations so decisions can be audited.
            </p>

            <form onSubmit={onSubmit} className="mt-6 rounded-2xl border border-stone-300 bg-white p-4">
              <label className="mb-2 block text-xs font-semibold uppercase tracking-wide text-stone-500">Try a query</label>
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full rounded-xl border border-stone-300 bg-stone-50 px-4 py-3 text-base text-stone-900 outline-none transition focus:border-teal-600"
                placeholder="Find senior engineers at Stripe"
              />
              <div className="mt-3 flex flex-wrap gap-2">
                <button className="rounded-xl bg-teal-700 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-teal-800" type="submit">
                  Run Search
                </button>
                <Link href="/features" className="rounded-xl border border-stone-300 px-5 py-2.5 text-sm font-semibold text-stone-700">
                  Explore Features
                </Link>
              </div>
            </form>

            <div className="mt-4 flex flex-wrap gap-2">
              {SUGGESTIONS.map((item) => (
                <Link key={item} href={`/search?q=${encodeURIComponent(item)}`} className="rounded-full border border-stone-300 bg-white px-4 py-2 text-sm text-stone-700 hover:border-teal-600 hover:text-teal-800">
                  {item}
                </Link>
              ))}
            </div>
          </div>
          <HeroVisuals />
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          <UsageCard
            title="Entity Resolution"
            description="Every workflow starts by resolving raw text to a canonical company/person to prevent noisy retrieval."
          />
          <UsageCard
            title="Citation-First Output"
            description="Every claim is expected to map back to source evidence. Empty evidence yields explicit degraded responses."
          />
          <UsageCard
            title="Operational Workflows"
            description="Use dedicated pages for search, signals, enrichment, and agent traces with one consistent navigation model."
          />
        </section>

        <section className="glass rounded-3xl p-6 md:p-8">
          <h2 className="font-display text-3xl text-stone-900">How to use CRMind in 3 steps</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            <Step title="1. Query precisely" text="Start with an account or person intent: role, company, and signal type." />
            <Step title="2. Inspect evidence" text="Review citations and confidence before acting. Treat degraded as a data gap, not a fact." />
            <Step title="3. Operationalize" text="Save entities, monitor signals, and enrich lead batches for outbound workflows." />
          </div>
        </section>
      </main>
      <PublicFooter />
    </div>
  );
}

function UsageCard({ title, description }: { title: string; description: string }) {
  return (
    <article className="glass rounded-2xl p-4">
      <h3 className="font-display text-xl text-stone-900">{title}</h3>
      <p className="mt-2 text-sm text-stone-700">{description}</p>
    </article>
  );
}

function Step({ title, text }: { title: string; text: string }) {
  return (
    <div className="rounded-2xl border border-stone-300/70 bg-white p-4">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-teal-800">{title}</h3>
      <p className="mt-2 text-sm text-stone-700">{text}</p>
    </div>
  );
}

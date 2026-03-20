"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

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
    <main className="relative min-h-screen overflow-hidden bg-stone-950 text-stone-100">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,#fb923c33_0%,transparent_35%),radial-gradient(circle_at_85%_80%,#fcd34d22_0%,transparent_40%)]" />
      <div className="relative mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-20">
        <p className="mb-6 inline-flex w-fit rounded-full border border-stone-700 bg-stone-900/80 px-3 py-1 text-xs uppercase tracking-[0.2em] text-amber-300">
          Search Gateway
        </p>
        <h1 className="max-w-4xl font-display text-5xl leading-tight md:text-7xl">
          Find accounts and people with evidence-backed intelligence.
        </h1>
        <p className="mt-6 max-w-2xl text-lg text-stone-300">
          CRMind resolves entities first, ranks trusted sources, and returns structured outputs with citations.
        </p>

        <form onSubmit={onSubmit} className="mt-10 rounded-2xl border border-stone-700 bg-stone-900/80 p-4 md:p-6">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full rounded-xl border border-stone-600 bg-stone-950 px-4 py-3 text-base text-stone-100 outline-none transition focus:border-amber-400"
            placeholder="Find senior engineers at Example Inc"
          />
          <button className="mt-3 rounded-xl bg-amber-500 px-5 py-3 font-semibold text-stone-950 transition hover:bg-amber-400" type="submit">
            Search CRMind
          </button>
        </form>

        <div className="mt-8 flex flex-wrap gap-2">
          {SUGGESTIONS.map((item) => (
            <Link key={item} href={`/search?q=${encodeURIComponent(item)}`} className="rounded-full border border-stone-600 px-4 py-2 text-sm text-stone-200 hover:border-amber-300 hover:text-amber-200">
              {item}
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}

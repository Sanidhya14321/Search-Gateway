"use client";

import { useEffect, useState } from "react";
import { getAccountBrief } from "@/lib/api/account";
import { SignalTimeline } from "@/components/signals/signal-timeline";
import { PersonCard } from "@/components/user/person-card";

export default function AccountBriefPage({ params }: { params: { id: string } }) {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getAccountBrief(params.id).then(setData).catch((e) => setError(String(e)));
  }, [params.id]);

  if (error) return <main className="text-red-600">{error}</main>;
  if (!data) return <main className="text-stone-600">Loading account brief...</main>;

  const result = data.result || data;

  return (
    <main className="space-y-6">
      <h1 className="font-display text-3xl text-stone-900">Account Brief</h1>
      <p className="text-stone-700">{result.summary || "No summary available."}</p>
      <SignalTimeline signals={result.signal_timeline || result.signals || []} />
      <section className="grid gap-3 md:grid-cols-2">
        {(result.people || []).map((person: any, idx: number) => (
          <PersonCard key={idx} person={person} />
        ))}
      </section>
    </main>
  );
}

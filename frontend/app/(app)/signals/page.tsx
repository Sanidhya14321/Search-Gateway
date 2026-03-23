"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet } from "@/lib/api/client";

const SIGNAL_COLORS: Record<string, string> = {
  hiring: "bg-emerald-900/50 text-emerald-300",
  funding: "bg-blue-900/50 text-blue-300",
  acquisition: "bg-amber-900/50 text-amber-300",
  restructuring: "bg-red-900/50 text-red-300",
  leadership_change: "bg-purple-900/50 text-purple-300",
};

export default function SignalsPage() {
  const [signals, setSignals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    async function loadSignals() {
      try {
        const saved = await apiGet("/api/v1/user/saved?limit=20&offset=0");
        const savedEntities = (saved.items || []) as Array<{ entity_id?: string; entity_name?: string }>;

        const signalResults = await Promise.all(
          savedEntities
            .filter((item) => Boolean(item.entity_id))
            .map(async (item) => {
              const response = await apiGet(`/api/v1/signals/${item.entity_id}?limit=10&offset=0`);
              return (response.items || []).map((signal: any) => ({
                ...signal,
                entity_id: item.entity_id,
                entity_name: item.entity_name,
              }));
            }),
        );

        setSignals(signalResults.flat());
      } catch (e) {
        console.error("Failed to load signals:", e);
      }

      setLoading(false);
    }

    loadSignals();
  }, []);

  const filteredSignals = filter === "all" 
    ? signals 
    : signals.filter((s) => s.signal_type === filter);

  if (loading) {
    return <main className="space-y-4"><div className="h-96 animate-pulse rounded bg-stone-700"></div></main>;
  }

  return (
    <main className="space-y-6">
      <header>
        <h1 className="font-display text-4xl font-bold text-stone-100">Signals</h1>
        <p className="mt-2 text-stone-400">Track hiring, funding, and other signals for your target accounts</p>
      </header>

      {/* Filter */}
      <div className="flex gap-2 flex-wrap">
        {["all", "hiring", "funding", "acquisition", "restructuring", "leadership_change"].map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`rounded-full px-4 py-2 text-sm transition ${
              filter === type ? "bg-amber-500 text-stone-950 font-semibold" : "border border-stone-600 text-stone-300 hover:bg-stone-800"
            }`}
          >
            {type === "all" ? "All Signals" : type.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      {filteredSignals.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {filteredSignals.map((signal: any) => (
            <Link
              key={signal.id}
              href={`/entity/${signal.entity_id}`}
              className="rounded-lg border border-stone-700 bg-stone-900/50 p-4 transition hover:bg-stone-800"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-stone-100">{signal.entity_name || "Unknown Entity"}</h3>
                  <p className="mt-1 text-sm text-stone-300">{signal.description}</p>
                  <p className="mt-2 text-xs text-stone-500">
                    {new Date(signal.detected_at).toLocaleDateString()}
                  </p>
                </div>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ml-3 whitespace-nowrap ${
                    SIGNAL_COLORS[signal.signal_type] || "bg-stone-700 text-stone-300"
                  }`}
                >
                  {signal.signal_type}
                </span>
              </div>
              {signal.source_url && (
                <a
                  href={signal.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-3 inline-text-xs text-amber-400 hover:underline"
                  onClick={(e) => e.stopPropagation()}
                >
                  View Source →
                </a>
              )}
            </Link>
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-stone-700 bg-stone-900/50 p-8 text-center">
          <p className="text-stone-400">No signals found</p>
        </div>
      )}
    </main>
  );
}

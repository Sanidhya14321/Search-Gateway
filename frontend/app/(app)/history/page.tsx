"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet } from "@/lib/api/client";

export default function HistoryPage() {
  const [searchHistory, setSearchHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadHistory() {
      try {
        const data = await apiGet("/api/v1/user/history");
        setSearchHistory(data.items || []);
      } catch (e) {
        console.error("Failed to load history:", e);
      }

      setLoading(false);
    }

    loadHistory();
  }, []);

  if (loading) {
    return <main className="space-y-4"><div className="h-96 animate-pulse rounded bg-stone-700"></div></main>;
  }

  return (
    <main className="space-y-6">
      <header>
        <h1 className="font-display text-4xl font-bold text-stone-100">Search History</h1>
        <p className="mt-2 text-stone-400">Your recent search queries</p>
      </header>

      {searchHistory.length > 0 ? (
        <div className="space-y-2">
          {searchHistory.map((item: any, idx: number) => (
            <Link
              key={`${item.created_at || idx}-${item.query || "q"}`}
              href={`/search?q=${encodeURIComponent(item.query)}`}
              className="block rounded-lg border border-stone-700 bg-stone-900/50 p-4 transition hover:bg-stone-800"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-stone-100">{item.query}</p>
                  <p className="text-xs text-stone-400">
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>
                <span className="text-xs rounded-full bg-stone-700 px-3 py-1">
                  {item.entity_type || "search"}
                </span>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-stone-700 bg-stone-900/50 p-8 text-center">
          <p className="text-stone-400">No search history yet</p>
          <Link href="/search" className="mt-4 inline-block rounded-lg bg-amber-500 px-6 py-2 font-semibold text-stone-950">
            Start Searching
          </Link>
        </div>
      )}
    </main>
  );
}

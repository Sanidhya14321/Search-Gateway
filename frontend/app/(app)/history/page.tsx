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
    return <main className="space-y-4"><div className="h-96 animate-pulse rounded bg-stone-200"></div></main>;
  }

  return (
    <main className="space-y-6">
      <header>
        <h1 className="font-display text-4xl font-bold text-stone-900">Search History</h1>
        <p className="mt-2 text-stone-600">Your recent search queries</p>
      </header>

      {searchHistory.length > 0 ? (
        <div className="space-y-2">
          {searchHistory.map((item: any, idx: number) => (
            <Link
              key={`${item.created_at || idx}-${item.query || "q"}`}
              href={`/search?q=${encodeURIComponent(item.query)}`}
              className="block rounded-lg border border-stone-200 bg-white/70 p-4 transition hover:border-stone-900"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-stone-900">{item.query}</p>
                  <p className="text-xs text-stone-500">
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>
                <span className="text-xs rounded-full bg-stone-100 px-3 py-1 text-stone-700">
                  {item.entity_type || "search"}
                </span>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-stone-200 bg-white/70 p-8 text-center">
          <p className="text-stone-600">No search history yet</p>
          <Link href="/search" className="mt-4 inline-block rounded-lg bg-stone-900 px-6 py-2 font-semibold text-white">
            Start Searching
          </Link>
        </div>
      )}
    </main>
  );
}

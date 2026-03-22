"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { createBrowserSupabaseClient } from "@/lib/supabase/client";

interface RecentSearch {
  id: string;
  query: string;
  entity_type: string;
  created_at: string;
}

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null);
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      const supabase = createBrowserSupabaseClient();
      
      // Get current user
      const { data: { user: authUser } } = await supabase.auth.getUser();
      setUser(authUser);

      // Try to fetch recent searches from API
      if (authUser?.id) {
        try {
          const resp = await fetch("/api/v1/user/history", {
            headers: { Authorization: `Bearer ${authUser.id}` },
          });
          if (resp.ok) {
            const data = await resp.json();
            setRecentSearches(data.items?.slice(0, 5) || []);
          }
        } catch (e) {
          console.error("Failed to fetch history:", e);
        }
      }
      
      setLoading(false);
    }

    loadData();
  }, []);

  if (loading) {
    return (
      <main className="space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-48 rounded bg-stone-700"></div>
          <div className="h-32 rounded bg-stone-700"></div>
        </div>
      </main>
    );
  }

  return (
    <main className="space-y-8">
      <header className="space-y-2">
        <h1 className="font-display text-4xl font-bold text-stone-100">
          Welcome, {user?.email?.split("@")[0] || "there"}
        </h1>
        <p className="text-stone-400">Run searches, manage enrichment jobs, and explore signals</p>
      </header>

      {/* Quick Actions */}
      <section className="grid gap-4 md:grid-cols-3">
        <Link
          href="/search"
          className="rounded-2xl border border-stone-700 bg-stone-900/70 p-6 transition hover:border-amber-500 hover:bg-stone-900"
        >
          <div className="text-3xl mb-2">🔍</div>
          <h2 className="font-semibold text-stone-100">Search</h2>
          <p className="text-sm text-stone-400">Find companies and people</p>
        </Link>
        <Link
          href="/enrich"
          className="rounded-2xl border border-stone-700 bg-stone-900/70 p-6 transition hover:border-amber-500 hover:bg-stone-900"
        >
          <div className="text-3xl mb-2">📋</div>
          <h2 className="font-semibold text-stone-100">Batch Enrich</h2>
          <p className="text-sm text-stone-400">Enrich lead lists</p>
        </Link>
        <Link
          href="/signals"
          className="rounded-2xl border border-stone-700 bg-stone-900/70 p-6 transition hover:border-amber-500 hover:bg-stone-900"
        >
          <div className="text-3xl mb-2">⚡</div>
          <h2 className="font-semibold text-stone-100">Signals</h2>
          <p className="text-sm text-stone-400">View hiring & funding signals</p>
        </Link>
      </section>

      {/* Recent Searches */}
      <section className="space-y-4">
        <h2 className="font-display text-2xl font-bold text-stone-100">Recent Searches</h2>
        {recentSearches.length > 0 ? (
          <div className="space-y-2">
            {recentSearches.map((search) => (
              <Link
                key={search.id}
                href={`/search?q=${encodeURIComponent(search.query)}`}
                className="block rounded-lg border border-stone-700 p-4 transition hover:bg-stone-800"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-stone-100">{search.query}</p>
                    <p className="text-xs text-stone-400">
                      {new Date(search.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className="text-xs rounded-full bg-stone-700 px-3 py-1">
                    {search.entity_type}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <p className="text-stone-400">No searches yet. Start by searching for a company or person.</p>
        )}
      </section>
    </main>
  );
}

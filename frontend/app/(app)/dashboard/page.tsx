"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { createBrowserSupabaseClient } from "@/lib/supabase/client";
import { apiGet } from "@/lib/api/client";

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
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function loadData() {
      try {
        const supabase = createBrowserSupabaseClient();
        
        // Get current user
        const { data: { user: authUser } } = await supabase.auth.getUser();
        if (!authUser) {
          setError("Not authenticated");
          setLoading(false);
          return;
        }
        setUser(authUser);

        // Try to fetch recent searches from API
        try {
          const data = await apiGet("/api/v1/user/history?limit=5&offset=0");
          setRecentSearches(data.items || []);
        } catch (apiError: any) {
          console.error("Failed to fetch history:", apiError);
          const errMsg = apiError?.message || String(apiError);
          if (errMsg.includes("localhost")) {
            setError("❌ Backend URL not configured. Set NEXT_PUBLIC_API_BASE_URL=https://crmind-api.onrender.com in Vercel env vars.");
          } else if (errMsg.includes("No active session")) {
            setError("❌ Authentication failed. Check NEXT_PUBLIC_SUPABASE_* env vars in Vercel.");
          } else if (errMsg.includes("CORS")) {
            setError(`❌ CORS Error: Backend blocked request. Set CORS_ALLOWED_ORIGINS on Render to include your Vercel URL. Error: ${errMsg}`);
          } else {
            setError(`❌ API Error: ${errMsg}`);
          }
        }
        
        setLoading(false);
      } catch (e: any) {
        console.error("Dashboard error:", e);
        setError(`❌ Failed to load dashboard: ${e?.message || String(e)}`);
        setLoading(false);
      }
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

  if (error) {
    return (
      <main className="space-y-6">
        <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-4">
          <p className="mb-4 text-sm text-red-200 whitespace-pre-wrap">{error}</p>
          <button 
            onClick={() => {
              setError("");
              setLoading(true);
              window.location.reload();
            }}
            className="rounded-lg bg-red-600 px-3 py-2 text-sm text-white hover:bg-red-700"
          >
            Retry
          </button>
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
            {recentSearches.map((search, idx) => (
              <Link
                key={`${search.created_at || idx}-${search.query || "q"}`}
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

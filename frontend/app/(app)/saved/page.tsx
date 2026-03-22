"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { createBrowserSupabaseClient } from "@/lib/supabase/client";

export default function SavedPage() {
  const [saved, setSaved] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSavedEntities() {
      const supabase = createBrowserSupabaseClient();
      const { data: { user } } = await supabase.auth.getUser();

      if (user?.id) {
        try {
          const resp = await fetch(`/api/v1/user/saved`, {
            headers: { Authorization: `Bearer ${user.id}` },
          });
          if (resp.ok) {
            const data = await resp.json();
            setSaved(data.items || []);
          }
        } catch (e) {
          console.error("Failed to load saved:", e);
        }
      }

      setLoading(false);
    }

    loadSavedEntities();
  }, []);

  if (loading) {
    return <main className="space-y-4"><div className="h-96 animate-pulse rounded bg-stone-700"></div></main>;
  }

  return (
    <main className="space-y-6">
      <header>
        <h1 className="font-display text-4xl font-bold text-stone-100">Saved Entities</h1>
        <p className="mt-2 text-stone-400">Your saved companies and contacts</p>
      </header>

      {saved.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {saved.map((entity: any) => (
            <Link
              key={entity.id}
              href={`/entity/${entity.id}`}
              className="rounded-lg border border-stone-700 bg-stone-900/50 p-6 transition hover:bg-stone-800"
            >
              <h3 className="font-semibold text-stone-100">{entity.name}</h3>
              <p className="mt-1 text-sm text-stone-400">{entity.type}</p>
              {entity.domain && <p className="mt-1 text-xs text-stone-500">{entity.domain}</p>}
              <p className="mt-3 text-xs text-stone-500">
                Saved {new Date(entity.saved_at).toLocaleDateString()}
              </p>
            </Link>
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-stone-700 bg-stone-900/50 p-8 text-center">
          <p className="text-stone-400">No saved entities yet</p>
          <Link href="/search" className="mt-4 inline-block rounded-lg bg-amber-500 px-6 py-2 font-semibold text-stone-950">
            Search & Save
          </Link>
        </div>
      )}
    </main>
  );
}

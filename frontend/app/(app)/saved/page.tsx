"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet } from "@/lib/api/client";

export default function SavedPage() {
  const [saved, setSaved] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSavedEntities() {
      try {
        const data = await apiGet("/api/v1/user/saved");
        setSaved(data.items || []);
      } catch (e) {
        console.error("Failed to load saved:", e);
      }

      setLoading(false);
    }

    loadSavedEntities();
  }, []);

  if (loading) {
    return <main className="space-y-4"><div className="h-96 animate-pulse rounded bg-stone-200"></div></main>;
  }

  return (
    <main className="space-y-6">
      <header>
        <h1 className="font-display text-4xl font-bold text-stone-900">Saved Entities</h1>
        <p className="mt-2 text-stone-600">Your saved companies and contacts</p>
      </header>

      {saved.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {saved.map((entity: any) => (
            <Link
              key={`${entity.entity_id}-${entity.entity_type}`}
              href={`/entity/${entity.entity_id}`}
              className="rounded-lg border border-stone-200 bg-white/70 p-6 transition hover:border-stone-900"
            >
              <h3 className="font-semibold text-stone-900">{entity.entity_name}</h3>
              <p className="mt-1 text-sm text-stone-600">{entity.entity_type}</p>
              {entity.domain && <p className="mt-1 text-xs text-stone-500">{entity.domain}</p>}
              <p className="mt-3 text-xs text-stone-500">
                Saved {new Date(entity.created_at).toLocaleDateString()}
              </p>
            </Link>
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-stone-200 bg-white/70 p-8 text-center">
          <p className="text-stone-600">No saved entities yet</p>
          <Link href="/search" className="mt-4 inline-block rounded-lg bg-stone-900 px-6 py-2 font-semibold text-white">
            Search & Save
          </Link>
        </div>
      )}
    </main>
  );
}

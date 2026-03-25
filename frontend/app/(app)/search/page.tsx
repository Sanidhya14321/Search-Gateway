"use client";

import dynamic from "next/dynamic";
import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { searchEntities } from "@/lib/api/search";

const EntityCard = dynamic(
  () => import("@/components/entity/entity-card").then((mod) => mod.EntityCard),
  { ssr: false },
);

export default function SearchPage() {
  const params = useSearchParams();
  const query = params.get("q") || "";

  const { data, isLoading, error } = useQuery({
    queryKey: ["search", query],
    queryFn: () => searchEntities(query),
    enabled: Boolean(query),
  });

  return (
    <main className="space-y-6">
      <h1 className="font-display text-3xl text-stone-900">Search Results</h1>
      {isLoading ? (
        <section className="grid gap-4 md:grid-cols-2">
          {Array.from({ length: 4 }).map((_, idx) => (
            <div key={idx} className="animate-pulse rounded-xl border border-stone-200 bg-white/80 p-4">
              <div className="h-5 w-40 rounded bg-stone-200" />
              <div className="mt-2 h-3 w-28 rounded bg-stone-200" />
              <div className="mt-4 h-3 w-full rounded bg-stone-200" />
              <div className="mt-2 h-3 w-2/3 rounded bg-stone-200" />
            </div>
          ))}
        </section>
      ) : null}
      {error ? <p className="text-red-600">{(error as Error).message}</p> : null}
      <section className="grid gap-4 md:grid-cols-2">
        {(data?.candidates || []).map((candidate: any) => (
          <EntityCard key={candidate.canonical_id} entity={candidate} />
        ))}
      </section>
    </main>
  );
}

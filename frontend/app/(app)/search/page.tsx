"use client";

import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { searchEntities } from "@/lib/api/search";
import { EntityCard } from "@/components/entity/entity-card";

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
      {isLoading ? <p className="text-stone-600">Loading...</p> : null}
      {error ? <p className="text-red-600">{(error as Error).message}</p> : null}
      <section className="grid gap-4 md:grid-cols-2">
        {(data?.candidates || []).map((candidate: any) => (
          <EntityCard key={candidate.canonical_id} entity={candidate} />
        ))}
      </section>
    </main>
  );
}

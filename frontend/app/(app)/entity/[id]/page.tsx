"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api/client";
import { CitationBadge } from "@/components/entity/citation-badge";

export default function EntityPage({ params }: { params: { id: string } }) {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiGet(`/api/v1/entity/${params.id}`).then(setData).catch((e) => setError(String(e)));
  }, [params.id]);

  if (error) return <main className="text-red-600">{error}</main>;
  if (!data) return <main className="text-stone-600">Loading entity...</main>;

  return (
    <main className="space-y-6">
      <h1 className="font-display text-3xl text-stone-900">{data.canonical_name}</h1>
      <p className="text-stone-700">{data.summary}</p>
      <div className="flex flex-wrap gap-2">
        {(data.citations || []).map((citation: any, idx: number) => <CitationBadge key={idx} citation={citation} />)}
      </div>
    </main>
  );
}

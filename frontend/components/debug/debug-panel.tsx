"use client";

import { useSearchParams } from "next/navigation";

type Chunk = {
  source_url?: string;
  similarity?: number;
  freshness_score?: number;
  trust_score?: number;
  final_score?: number;
};

type Props = {
  steps: string[];
  chunks: Chunk[];
  cacheHit: boolean;
  durationMs: number;
};

export function DebugPanel({ steps, chunks, cacheHit, durationMs }: Props) {
  const params = useSearchParams();
  if (params.get("debug") !== "true") return null;

  return (
    <details className="rounded-xl border border-stone-700 bg-stone-900/80 p-4">
      <summary className="cursor-pointer font-semibold text-stone-100">Debug Panel</summary>
      <div className="mt-3 space-y-4 text-sm text-stone-200">
        <section>
          <p className="mb-2 font-semibold">Agent Steps</p>
          <ul className="space-y-1">
            {steps.map((step, idx) => (
              <li key={`${step}-${idx}`} className="rounded bg-stone-800 px-2 py-1">{step}</li>
            ))}
          </ul>
        </section>
        <section>
          <p className="mb-2 font-semibold">Retrieved Chunks</p>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead className="text-stone-400"><tr><th className="text-left">source</th><th>sim</th><th>fresh</th><th>trust</th><th>score</th></tr></thead>
              <tbody>
                {chunks.map((chunk, idx) => (
                  <tr key={idx} className="border-t border-stone-700">
                    <td className="py-1">{chunk.source_url || "n/a"}</td>
                    <td className="text-center">{chunk.similarity?.toFixed(2) || "-"}</td>
                    <td className="text-center">{chunk.freshness_score?.toFixed(2) || "-"}</td>
                    <td className="text-center">{chunk.trust_score?.toFixed(2) || "-"}</td>
                    <td className="text-center">{chunk.final_score?.toFixed(2) || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
        <section className="flex gap-2">
          <span className={`rounded-full px-2 py-1 text-xs ${cacheHit ? "bg-emerald-700 text-emerald-100" : "bg-amber-700 text-amber-100"}`}>
            Cache {cacheHit ? "HIT" : "MISS"}
          </span>
          <span className="rounded-full bg-stone-700 px-2 py-1 text-xs">{durationMs} ms</span>
        </section>
      </div>
    </details>
  );
}

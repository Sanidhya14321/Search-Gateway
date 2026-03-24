import Link from "next/link";
import type { SearchCandidate } from "@/types/api";

export function EntityCard({ entity }: { entity: SearchCandidate }) {
  return (
    <article className="rounded-xl border border-stone-200 bg-white/80 p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-display text-lg text-stone-900">{entity.canonical_name}</h3>
          <p className="text-xs text-stone-500">{entity.canonical_id}</p>
        </div>
        <span className="rounded-full bg-stone-900 px-2 py-1 text-xs font-semibold text-white">
          {(entity.confidence * 100).toFixed(0)}%
        </span>
      </div>
      <div className="mt-3 flex items-center justify-between text-sm text-stone-700">
        <span>{entity.domain || "-"}</span>
        <span className="uppercase tracking-wide text-stone-500">{entity.match_type || "match"}</span>
      </div>
      <Link className="mt-4 inline-block text-sm text-teal-700 hover:text-teal-900" href={`/entity/${entity.canonical_id}`}>
        Open entity
      </Link>
    </article>
  );
}

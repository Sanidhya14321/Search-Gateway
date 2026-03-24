import type { Citation } from "@/types/api";

export function CitationBadge({ citation }: { citation: Citation }) {
  const host = citation.url ? new URL(citation.url).hostname.replace("www.", "") : "source";
  return (
    <a href={citation.url} target="_blank" rel="noreferrer" className="inline-flex rounded-full border border-stone-300 bg-white/80 px-3 py-1 text-xs text-stone-700 hover:border-stone-900">
      {host} • trust {citation.trust_score?.toFixed(2) ?? "-"}
    </a>
  );
}

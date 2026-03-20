import { CitationBadge } from "@/components/entity/citation-badge";

type Person = {
  full_name: string;
  current_title?: string;
  seniority_level?: string;
  citations?: Array<{ url: string; trust_score?: number }>;
};

export function PersonCard({ person }: { person: Person }) {
  return (
    <article className="rounded-xl border border-stone-700 bg-stone-900/80 p-4">
      <h3 className="font-semibold text-stone-100">{person.full_name}</h3>
      <p className="text-sm text-stone-300">{person.current_title || "Unknown title"}</p>
      <span className="mt-2 inline-block rounded-full bg-stone-800 px-2 py-1 text-xs text-stone-300">{person.seniority_level || "unknown"}</span>
      <div className="mt-3 flex flex-wrap gap-2">
        {(person.citations || []).map((citation, idx) => (
          <CitationBadge key={idx} citation={citation} />
        ))}
      </div>
    </article>
  );
}

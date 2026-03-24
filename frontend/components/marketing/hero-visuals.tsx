export function HeroVisuals() {
  return (
    <div className="space-y-4">
      <div className="glass rounded-2xl p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-stone-500">Pipeline Score Lens</p>
        <div className="mt-3 space-y-2">
          <Metric label="Semantic relevance" value={86} />
          <Metric label="Freshness" value={72} />
          <Metric label="Source trust" value={79} />
          <Metric label="Authority" value={68} />
        </div>
      </div>

      <div className="glass rounded-2xl p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-stone-500">System Tree</p>
        <pre className="mt-3 overflow-x-auto rounded-xl border border-stone-300/70 bg-white/70 p-3 text-xs text-stone-700">
{`User Query
  -> Entity Resolver
    -> Canonical Company/Person
      -> Retrieval Layer
        -> Vector Search
        -> Keyword Search
      -> Ranker (freshness + trust)
        -> Agent Synthesis
          -> Citation Formatter
            -> Structured JSON Output`}
        </pre>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs text-stone-600">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-2 rounded-full bg-stone-200">
        <div className="h-full rounded-full bg-teal-700" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import { runAgent } from "@/lib/api/agent";

const DebugPanel = dynamic(
  () => import("@/components/debug/debug-panel").then((mod) => mod.DebugPanel),
  { ssr: false },
);

const WORKFLOWS = ["lead_finder", "account_brief", "crm_enrichment", "research", "ops_debug"];

export default function AgentPage() {
  const [workflow, setWorkflow] = useState(WORKFLOWS[0]);
  const [query, setQuery] = useState("Find senior engineers at Stripe");
  const [result, setResult] = useState<any>(null);
  const [steps, setSteps] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setRunning(true);
    setError("");
    setResult(null);
    setSteps([]);

    try {
      const response = await runAgent(workflow, query);
      setResult(response.result || response);
      setSteps(response.steps_log || []);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setRunning(false);
    }
  }

  return (
    <main className="space-y-6">
      <h1 className="font-display text-3xl text-stone-900">Agent Runner</h1>
      <form onSubmit={submit} className="glass rounded-xl p-4">
        <select className="rounded-lg border border-stone-300 bg-white px-3 py-2 text-stone-800" value={workflow} onChange={(e) => setWorkflow(e.target.value)}>
          {WORKFLOWS.map((item) => (
            <option key={item} value={item}>{item}</option>
          ))}
        </select>
        <textarea className="mt-3 block w-full rounded-lg border border-stone-300 bg-white p-3 text-stone-800" rows={4} value={query} onChange={(e) => setQuery(e.target.value)} />
        <button disabled={running} className="mt-3 rounded-lg bg-stone-900 px-4 py-2 font-semibold text-white disabled:opacity-60">
          {running ? "Running..." : "Run Agent"}
        </button>
      </form>
      {error ? <p className="text-red-600">{error}</p> : null}
      {running && !result ? (
        <div className="animate-pulse rounded-xl border border-stone-200 bg-white/90 p-4">
          <div className="h-4 w-40 rounded bg-stone-200" />
          <div className="mt-3 h-3 w-full rounded bg-stone-200" />
          <div className="mt-2 h-3 w-5/6 rounded bg-stone-200" />
          <div className="mt-2 h-3 w-4/6 rounded bg-stone-200" />
        </div>
      ) : null}
      {result ? <pre className="overflow-x-auto rounded-xl border border-stone-200 bg-white/90 p-4 text-xs text-stone-800">{JSON.stringify(result, null, 2)}</pre> : null}
      <DebugPanel steps={steps} chunks={result?.ranked_chunks || []} cacheHit={Boolean(result?.cache_hit)} durationMs={result?.duration_ms || 0} />
    </main>
  );
}

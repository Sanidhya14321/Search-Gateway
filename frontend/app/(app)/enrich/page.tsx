"use client";

import { useState } from "react";
import Link from "next/link";
import { apiGet, apiPost } from "@/lib/api/client";

interface Lead {
  name: string;
  company: string;
  email?: string;
  title?: string;
}

export default function EnrichPage() {
  const [leads, setLeads] = useState<Lead[]>([{ name: "", company: "", email: "", title: "" }]);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "submitting" | "polling">( "idle");
  const [jobStatus, setJobStatus] = useState<any>(null);
  const [error, setError] = useState("");

  const addLead = () => {
    setLeads([...leads, { name: "", company: "", email: "", title: "" }]);
  };

  const updateLead = (index: number, field: keyof Lead, value: string) => {
    const updated = [...leads];
    updated[index][field] = value;
    setLeads(updated);
  };

  const removeLead = (index: number) => {
    setLeads(leads.filter((_, i) => i !== index));
  };

  const submitEnrich = async (e: React.FormEvent) => {
    e.preventDefault();
    if (leads.some((l) => !l.name || !l.company)) {
      setError("All leads must have name and company");
      return;
    }

    setStatus("submitting");
    setError("");

    try {
      const data = await apiPost("/api/v1/enrich/batch", { leads });
      setJobId(data.job_id);
      setStatus("polling");

      // Poll for completion
      let attempts = 0;
      while (attempts < 60) {
        const jobData = await apiGet(`/api/v1/enrich/batch/${data.job_id}`);
        setJobStatus(jobData);

        if (jobData.status === "completed") {
          setStatus("idle");
          break;
        }

        await new Promise((resolve) => setTimeout(resolve, 1000));
        attempts++;
      }
    } catch (e) {
      setError((e as Error).message);
      setStatus("idle");
    }
  };

  return (
    <main className="space-y-6">
      <header>
        <h1 className="font-display text-4xl font-bold text-stone-900">Batch Enrichment</h1>
        <p className="mt-2 text-stone-600">Upload leads to enrich with company and contact data</p>
      </header>

      <form onSubmit={submitEnrich} className="space-y-4 rounded-lg border border-stone-200 bg-white/80 p-6">
        <div className="space-y-3">
          {leads.map((lead, idx) => (
            <div key={idx} className="grid gap-2 md:grid-cols-5">
              <input
                placeholder="Name"
                value={lead.name}
                onChange={(e) => updateLead(idx, "name", e.target.value)}
                className="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800"
              />
              <input
                placeholder="Company"
                value={lead.company}
                onChange={(e) => updateLead(idx, "company", e.target.value)}
                className="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800"
              />
              <input
                placeholder="Email (optional)"
                type="email"
                value={lead.email || ""}
                onChange={(e) => updateLead(idx, "email", e.target.value)}
                className="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800"
              />
              <input
                placeholder="Title (optional)"
                value={lead.title || ""}
                onChange={(e) => updateLead(idx, "title", e.target.value)}
                className="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800"
              />
              <button
                type="button"
                onClick={() => removeLead(idx)}
                className="rounded-lg border border-stone-300 text-stone-700 hover:border-stone-900"
              >
                Remove
              </button>
            </div>
          ))}
        </div>

        <button
          type="button"
          onClick={addLead}
          className="rounded-lg border border-stone-300 px-4 py-2 text-sm text-stone-700 hover:border-stone-900"
        >
          + Add Lead
        </button>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          disabled={status !== "idle"}
          className="w-full rounded-lg bg-stone-900 px-4 py-3 font-semibold text-white disabled:opacity-60"
        >
          {status === "submitting" ? "Submitting..." : status === "polling" ? "Processing..." : "Enrich Leads"}
        </button>
      </form>

      {jobStatus && (
        <div className="rounded-lg border border-stone-200 bg-white/80 p-6">
          <h2 className="font-semibold text-stone-900">Job Status: {jobStatus.status}</h2>
          {jobStatus.status === "completed" && jobStatus.result?.enriched_rows && (
            <div className="mt-4 space-y-2">
              {jobStatus.result.enriched_rows.map((row: any, idx: number) => (
                <Link
                  key={idx}
                  href={`/entity/${row.canonical_id || row.entity_id || ""}`}
                  className="block rounded-lg border border-stone-200 p-3 text-sm text-stone-800 hover:border-stone-900"
                >
                  {row.canonical_name || row.full_name || row.canonical_id || "Enriched row"}
                </Link>
              ))}
            </div>
          )}
        </div>
      )}
    </main>
  );
}

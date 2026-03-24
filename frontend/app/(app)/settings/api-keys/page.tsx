"use client";

import { useEffect, useState } from "react";
import { apiDelete, apiGet, apiPost } from "@/lib/api/client";

interface ApiKey {
  id: string;
  key_prefix: string;
  name: string;
  created_at: string;
  last_used_at: string | null;
}

export default function ApiKeysPage() {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newKey, setNewKey] = useState<string | null>(null);

  useEffect(() => {
    async function loadKeys() {
      try {
        const data = await apiGet("/api/v1/auth/api-keys");
        setApiKeys(data.api_keys || []);
      } catch (e) {
        console.error("Failed to load API keys:", e);
      }

      setLoading(false);
    }

    loadKeys();
  }, []);

  const createNewKey = async () => {
    setCreating(true);

    try {
      const data = await apiPost(`/api/v1/auth/api-keys`, {
        name: `UI Key ${new Date().toISOString().slice(0, 10)}`,
      });
      setNewKey(data.raw_key);
      setApiKeys([
        ...apiKeys,
        {
          id: data.id,
          key_prefix: data.key_prefix,
          name: data.name,
          created_at: data.created_at,
          last_used_at: null,
        },
      ]);
    } catch (e) {
      console.error("Failed to create key:", e);
    }

    setCreating(false);
  };

  const revokeKey = async (keyId: string) => {
    try {
      await apiDelete(`/api/v1/auth/api-keys/${keyId}`);

      setApiKeys(apiKeys.filter((k) => k.id !== keyId));
    } catch (e) {
      console.error("Failed to revoke key:", e);
    }
  };

  if (loading) {
    return <main className="space-y-4"><div className="h-96 animate-pulse rounded-2xl bg-stone-200"></div></main>;
  }

  return (
    <main className="max-w-4xl space-y-8">
      <header>
        <h1 className="font-display text-4xl font-bold text-stone-900">API Keys</h1>
        <p className="mt-2 text-stone-600">Create, rotate, and revoke keys for programmatic access from scripts, CRON jobs, and integrations.</p>
      </header>

      <section className="glass rounded-2xl p-5 space-y-4">
        <h2 className="font-display text-2xl text-stone-900">Create a key</h2>
        <button
          onClick={createNewKey}
          disabled={creating}
          className="rounded-lg bg-stone-900 px-6 py-2 font-semibold text-white disabled:opacity-60"
        >
          {creating ? "Creating..." : "+ Create API Key"}
        </button>
      </section>

      {newKey && (
        <div className="rounded-2xl border border-emerald-300 bg-emerald-50 p-4 space-y-2">
          <p className="font-semibold text-emerald-800">New API Key Created</p>
          <p className="text-xs text-emerald-900">Copy this key now. You will not be able to view it again after this screen.</p>
          <code className="block rounded bg-white p-3 font-mono text-xs text-emerald-900 break-all border border-emerald-200">
            {newKey}
          </code>
          <button
            onClick={() => {
              navigator.clipboard.writeText(newKey);
              alert("Copied to clipboard!");
            }}
            className="rounded-lg border border-emerald-500 px-3 py-1 text-xs text-emerald-800 hover:bg-emerald-100"
          >
            Copy to Clipboard
          </button>
        </div>
      )}

      <section className="glass rounded-2xl p-5 space-y-4">
        <h2 className="font-display text-2xl text-stone-900">How to use your key</h2>
        <p className="text-sm text-stone-700">Send your key in the Authorization header with the Bearer scheme.</p>
        <pre className="overflow-x-auto rounded-lg border border-stone-200 bg-white p-3 text-xs text-stone-700">
{`curl -X POST "$NEXT_PUBLIC_API_BASE_URL/api/v1/agent/run" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"workflow":"research","query":"Recent hiring signals for Stripe"}'`}
        </pre>
        <pre className="overflow-x-auto rounded-lg border border-stone-200 bg-white p-3 text-xs text-stone-700">
{`const res = await fetch("/api/v1/search?q=hubspot", {
  headers: { Authorization: "Bearer " + process.env.CRMIND_API_KEY }
});`}
        </pre>
      </section>

      {apiKeys.length > 0 ? (
        <section className="glass rounded-2xl p-5 space-y-3">
          <h2 className="font-display text-2xl text-stone-900">Active keys</h2>
          {apiKeys.map((key) => (
            <div key={key.id} className="flex items-center justify-between rounded-lg border border-stone-200 bg-white/80 p-4">
              <div>
                <p className="font-mono text-sm text-stone-700">{key.key_prefix}...</p>
                <p className="text-xs text-stone-600">{key.name}</p>
                <p className="text-xs text-stone-500">
                  Created {new Date(key.created_at).toLocaleDateString()}
                  {key.last_used_at && ` · Last used ${new Date(key.last_used_at).toLocaleDateString()}`}
                </p>
              </div>
              <button
                onClick={() => revokeKey(key.id)}
                className="rounded-lg border border-red-300 px-3 py-1 text-xs text-red-700 hover:bg-red-50"
              >
                Revoke
              </button>
            </div>
          ))}
        </section>
      ) : (
        <p className="text-stone-600">No API keys created yet.</p>
      )}

      <section className="glass rounded-2xl p-5 space-y-2">
        <h2 className="font-display text-2xl text-stone-900">Security best practices</h2>
        <ul className="space-y-1 text-sm text-stone-700">
          <li>Store keys in environment variables, never hard-code them in frontend files.</li>
          <li>Create separate keys for local development and production integrations.</li>
          <li>Rotate keys periodically and revoke immediately if leaked.</li>
          <li>Use diagnostics and backend logs to monitor unexpected usage patterns.</li>
        </ul>
      </section>
    </main>
  );
}

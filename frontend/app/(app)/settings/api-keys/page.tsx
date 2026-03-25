"use client";

import { useEffect, useState } from "react";
import { apiDelete, apiGet, apiPost } from "@/lib/api/client";

interface ApiKey {
  id: string;
  key_prefix: string;
  name: string;
  created_at: string;
  last_used_at: string | null;
  expires_at?: string | null;
}

export default function ApiKeysPage() {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [rotatingKeyId, setRotatingKeyId] = useState<string | null>(null);
  const [newKey, setNewKey] = useState<string | null>(null);
  const [keyName, setKeyName] = useState(`UI Key ${new Date().toISOString().slice(0, 10)}`);
  const [expiresInDays, setExpiresInDays] = useState<string>("30");
  const [error, setError] = useState<string>("");

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
    if (!keyName.trim()) {
      setError("API key name is required");
      return;
    }

    setCreating(true);
    setError("");

    try {
      const data = await apiPost(`/api/v1/auth/api-keys`, {
        name: keyName.trim(),
        expires_in_days: expiresInDays ? Number(expiresInDays) : undefined,
      });
      setNewKey(data.raw_key);
      setApiKeys((prev) => [
        {
          id: data.id,
          key_prefix: data.key_prefix,
          name: data.name,
          created_at: data.created_at,
          last_used_at: null,
          expires_at: data.expires_at,
        },
        ...prev,
      ]);
      setKeyName(`UI Key ${new Date().toISOString().slice(0, 10)}`);
    } catch (e) {
      console.error("Failed to create key:", e);
      setError((e as Error)?.message || "Failed to create API key");
    }

    setCreating(false);
  };

  const revokeKey = async (keyId: string) => {
    try {
      await apiDelete(`/api/v1/auth/api-keys/${keyId}`);

      setApiKeys((prev) => prev.filter((k) => k.id !== keyId));
    } catch (e) {
      console.error("Failed to revoke key:", e);
      setError((e as Error)?.message || "Failed to revoke API key");
    }
  };

  const rotateKey = async (key: ApiKey) => {
    setRotatingKeyId(key.id);
    setError("");
    try {
      const data = await apiPost(`/api/v1/auth/api-keys`, {
        name: `${key.name} (rotated ${new Date().toISOString().slice(0, 10)})`,
        expires_in_days: expiresInDays ? Number(expiresInDays) : undefined,
      });
      await apiDelete(`/api/v1/auth/api-keys/${key.id}`);

      setNewKey(data.raw_key);
      setApiKeys((prev) => [
        {
          id: data.id,
          key_prefix: data.key_prefix,
          name: data.name,
          created_at: data.created_at,
          last_used_at: null,
          expires_at: data.expires_at,
        },
        ...prev.filter((item) => item.id !== key.id),
      ]);
    } catch (e) {
      console.error("Failed to rotate key:", e);
      setError((e as Error)?.message || "Failed to rotate API key");
    } finally {
      setRotatingKeyId(null);
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
        <div className="grid gap-3 md:grid-cols-2">
          <label className="text-sm text-stone-700">
            Key name
            <input
              value={keyName}
              onChange={(e) => setKeyName(e.target.value)}
              placeholder="Production CI key"
              className="mt-1 w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800"
            />
          </label>
          <label className="text-sm text-stone-700">
            Expiration
            <select
              value={expiresInDays}
              onChange={(e) => setExpiresInDays(e.target.value)}
              className="mt-1 w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800"
            >
              <option value="">No expiration</option>
              <option value="7">7 days</option>
              <option value="30">30 days</option>
              <option value="90">90 days</option>
              <option value="180">180 days</option>
              <option value="365">365 days</option>
            </select>
          </label>
        </div>
        <button
          onClick={createNewKey}
          disabled={creating}
          className="rounded-lg bg-stone-900 px-6 py-2 font-semibold text-white disabled:opacity-60"
        >
          {creating ? "Creating..." : "+ Create API Key"}
        </button>
        {error ? <p className="text-sm text-red-600">{error}</p> : null}
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
                  {key.expires_at && ` · Expires ${new Date(key.expires_at).toLocaleDateString()}`}
                  {key.last_used_at && ` · Last used ${new Date(key.last_used_at).toLocaleDateString()}`}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => rotateKey(key)}
                  disabled={rotatingKeyId === key.id}
                  className="rounded-lg border border-stone-300 px-3 py-1 text-xs text-stone-700 hover:border-stone-900 disabled:opacity-60"
                >
                  {rotatingKeyId === key.id ? "Rotating..." : "Rotate"}
                </button>
                <button
                  onClick={() => revokeKey(key.id)}
                  className="rounded-lg border border-red-300 px-3 py-1 text-xs text-red-700 hover:bg-red-50"
                >
                  Revoke
                </button>
              </div>
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

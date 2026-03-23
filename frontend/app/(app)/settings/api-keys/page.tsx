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
    return <main className="space-y-4"><div className="h-96 animate-pulse rounded bg-stone-700"></div></main>;
  }

  return (
    <main className="max-w-2xl space-y-8">
      <header>
        <h1 className="font-display text-4xl font-bold text-stone-100">API Keys</h1>
        <p className="mt-2 text-stone-400">Manage API keys for programmatic access</p>
      </header>

      <button
        onClick={createNewKey}
        disabled={creating}
        className="rounded-lg bg-amber-500 px-6 py-2 font-semibold text-stone-950 disabled:opacity-60"
      >
        {creating ? "Creating..." : "+ Create API Key"}
      </button>

      {newKey && (
        <div className="rounded-lg border border-emerald-700/50 bg-emerald-900/10 p-4 space-y-2">
          <p className="font-semibold text-emerald-300">New API Key Created</p>
          <p className="text-xs text-stone-400">Copy this key now. You won't be able to see it again.</p>
          <code className="block rounded bg-stone-900 p-3 font-mono text-xs text-emerald-300 break-all">
            {newKey}
          </code>
          <button
            onClick={() => {
              navigator.clipboard.writeText(newKey);
              alert("Copied to clipboard!");
            }}
            className="rounded-lg border border-emerald-600 px-3 py-1 text-xs text-emerald-300 hover:bg-emerald-900/20"
          >
            Copy to Clipboard
          </button>
        </div>
      )}

      {apiKeys.length > 0 ? (
        <div className="space-y-2">
          {apiKeys.map((key) => (
            <div key={key.id} className="flex items-center justify-between rounded-lg border border-stone-700 bg-stone-900/50 p-4">
              <div>
                <p className="font-mono text-sm text-stone-300">{key.key_prefix}...</p>
                <p className="text-xs text-stone-400">{key.name}</p>
                <p className="text-xs text-stone-500">
                  Created {new Date(key.created_at).toLocaleDateString()}
                  {key.last_used_at && ` · Last used ${new Date(key.last_used_at).toLocaleDateString()}`}
                </p>
              </div>
              <button
                onClick={() => revokeKey(key.id)}
                className="rounded-lg border border-red-600 px-3 py-1 text-xs text-red-300 hover:bg-red-900/20"
              >
                Revoke
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-stone-400">No API keys created yet</p>
      )}
    </main>
  );
}

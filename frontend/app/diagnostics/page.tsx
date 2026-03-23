"use client";

import { useEffect, useState } from "react";
import { buildApiUrl } from "@/lib/api/client";

export default function DiagnosticsPage() {
  const [diags, setDiags] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function runDiagnostics() {
      const results: Record<string, any> = {};

      // Check environment variables
      results.env = {
        NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || "❌ NOT SET",
        NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL || "ℹ️ OPTIONAL",
      };

      const token = typeof window !== "undefined" ? window.localStorage.getItem("crmind_access_token") : null;
      results.auth = {
        tokenPresent: Boolean(token),
      };

      // Check backend connectivity
      if (process.env.NEXT_PUBLIC_API_BASE_URL) {
        try {
          const apiUrl = (process.env.NEXT_PUBLIC_API_BASE_URL || "").replace(/\/+$/, "");
          const response = await fetch(`${apiUrl}/api/v1/health`, {
            method: "GET",
            cache: "no-store",
          });
          results.backend = {
            url: apiUrl,
            reachable: response.ok,
            status: response.status,
          };
        } catch (e) {
          results.backend = {
            url: process.env.NEXT_PUBLIC_API_BASE_URL,
            reachable: false,
            error: String(e),
          };
        }
      } else {
        results.backend = { error: "NEXT_PUBLIC_API_BASE_URL not set" };
      }

      if (token) {
        try {
          const response = await fetch(buildApiUrl("/api/v1/auth/me"), {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
            },
            cache: "no-store",
          });

          if (!response.ok) {
            results.auth.currentUser = null;
            results.auth.authCheckError = `HTTP ${response.status}`;
          } else {
            const me = await response.json();
            results.auth.currentUser = {
              id: me.id,
              email: me.email,
            };
          }
        } catch (e) {
          results.auth.currentUser = null;
          results.auth.authCheckError = String(e);
        }
      }

      setDiags(results);
      setLoading(false);
    }

    runDiagnostics();
  }, []);

  if (loading) return <div className="p-4">Running diagnostics...</div>;

  return (
    <main className="min-h-screen bg-stone-950 p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-stone-100">🔍 Diagnostics</h1>

        <section className="space-y-4">
          <h2 className="text-xl font-semibold text-stone-200">Environment Variables</h2>
          <div className="rounded-lg bg-stone-900 p-4 space-y-2 text-sm font-mono">
            {Object.entries(diags.env || {}).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-stone-400">{key}:</span>
                <span className={typeof value === "string" && value.startsWith("❌") ? "text-red-400" : "text-green-400"}>
                  {String(value)}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-4">
          <h2 className="text-xl font-semibold text-stone-200">Auth Status</h2>
          <div className="rounded-lg bg-stone-900 p-4 space-y-2 text-sm">
            <div>
              Access Token: <span className={diags.auth?.tokenPresent ? "text-green-400" : "text-red-400"}>{diags.auth?.tokenPresent ? "✅ present" : "❌ missing"}</span>
            </div>
            <div>
              Current User: <span className={diags.auth?.currentUser ? "text-green-400" : "text-orange-400"}>{diags.auth?.currentUser ? diags.auth.currentUser.email : "Not resolved"}</span>
            </div>
            {diags.auth?.authCheckError && <div className="text-red-400 mt-2">Error: {diags.auth.authCheckError}</div>}
          </div>
        </section>

        <section className="space-y-4">
          <h2 className="text-xl font-semibold text-stone-200">Backend Connectivity</h2>
          <div className="rounded-lg bg-stone-900 p-4 space-y-2 text-sm">
            <div>
              URL: <span className="text-stone-300 font-mono">{diags.backend?.url || "NOT SET"}</span>
            </div>
            <div>
              Reachable: <span className={diags.backend?.reachable ? "text-green-400" : "text-red-400"}>{diags.backend?.reachable ? "✅" : "❌"}</span>
            </div>
            {diags.backend?.status && <div>Status Code: {diags.backend.status}</div>}
            {diags.backend?.error && <div className="text-red-400 mt-2">Error: {diags.backend.error}</div>}
          </div>
        </section>

        <section className="rounded-lg bg-blue-900/30 border border-blue-500/40 p-4">
          <h3 className="font-semibold text-blue-200 mb-2">💡 What to check:</h3>
          <ul className="text-sm text-blue-100 space-y-1">
            {!diags.backend?.reachable && <li>• Check NEXT_PUBLIC_API_BASE_URL is correct and backend is running</li>}
            {!diags.backend?.reachable && <li>• Check backend CORS_ALLOWED_ORIGINS includes your frontend domain</li>}
            {!diags.auth?.tokenPresent && <li>• Sign in again to generate a local JWT token</li>}
            {diags.auth?.authCheckError && <li>• Ensure AUTH_JWT_SECRET is set and consistent for login + auth verification</li>}
          </ul>
        </section>
      </div>
    </main>
  );
}

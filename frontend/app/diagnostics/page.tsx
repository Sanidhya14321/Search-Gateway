"use client";

import { useEffect, useState } from "react";
import { buildApiUrl } from "@/lib/api/client";
import { PageGuide } from "@/components/common/page-guide";
import { PublicFooter } from "@/components/layout/public-footer";
import { PublicNav } from "@/components/layout/public-nav";

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

  if (loading) {
    return (
      <div className="page-wrap">
        <PublicNav />
        <main className="page-container">
          <div className="glass rounded-2xl p-6 text-sm text-stone-700">Running diagnostics...</div>
        </main>
      </div>
    );
  }

  return (
    <div className="page-wrap">
      <PublicNav />
      <main className="page-container max-w-4xl space-y-6">
        <PageGuide
          title="Diagnostics"
          description="Use this page to quickly verify auth state, backend connectivity, and environment configuration before deeper debugging."
          howToUse={[
            "Confirm backend reachability first.",
            "Validate token presence and /auth/me resolution.",
            "Copy diagnostics output when opening support tickets.",
          ]}
        />

        <section className="space-y-4">
          <h2 className="font-display text-2xl text-stone-900">Environment Variables</h2>
          <div className="glass rounded-2xl p-4 space-y-2 text-sm font-mono">
            {Object.entries(diags.env || {}).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-stone-500">{key}:</span>
                <span className={typeof value === "string" && value.startsWith("❌") ? "text-red-400" : "text-green-400"}>
                  {String(value)}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-4">
          <h2 className="font-display text-2xl text-stone-900">Auth Status</h2>
          <div className="glass rounded-2xl p-4 space-y-2 text-sm">
            <div>
              Access Token: <span className={diags.auth?.tokenPresent ? "text-green-700" : "text-red-500"}>{diags.auth?.tokenPresent ? "present" : "missing"}</span>
            </div>
            <div>
              Current User: <span className={diags.auth?.currentUser ? "text-green-700" : "text-amber-700"}>{diags.auth?.currentUser ? diags.auth.currentUser.email : "Not resolved"}</span>
            </div>
            {diags.auth?.authCheckError && <div className="text-red-400 mt-2">Error: {diags.auth.authCheckError}</div>}
          </div>
        </section>

        <section className="space-y-4">
          <h2 className="font-display text-2xl text-stone-900">Backend Connectivity</h2>
          <div className="glass rounded-2xl p-4 space-y-2 text-sm">
            <div>
              URL: <span className="text-stone-700 font-mono">{diags.backend?.url || "NOT SET"}</span>
            </div>
            <div>
              Reachable: <span className={diags.backend?.reachable ? "text-green-700" : "text-red-500"}>{diags.backend?.reachable ? "yes" : "no"}</span>
            </div>
            {diags.backend?.status && <div>Status Code: {diags.backend.status}</div>}
            {diags.backend?.error && <div className="text-red-500 mt-2">Error: {diags.backend.error}</div>}
          </div>
        </section>

        <section className="glass rounded-2xl border border-sky-200 p-4">
          <h3 className="font-semibold text-sky-800 mb-2">What to check next</h3>
          <ul className="text-sm text-sky-900 space-y-1">
            {!diags.backend?.reachable && <li>• Check NEXT_PUBLIC_API_BASE_URL is correct and backend is running</li>}
            {!diags.backend?.reachable && <li>• Check backend CORS_ALLOWED_ORIGINS includes your frontend domain</li>}
            {!diags.auth?.tokenPresent && <li>• Sign in again to generate a local JWT token</li>}
            {diags.auth?.authCheckError && <li>• Ensure AUTH_JWT_SECRET is set and consistent for login + auth verification</li>}
          </ul>
        </section>
      </main>
      <PublicFooter />
    </div>
  );
}

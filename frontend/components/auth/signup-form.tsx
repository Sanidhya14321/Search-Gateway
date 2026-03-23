"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { createBrowserSupabaseClient } from "@/lib/supabase/client";
import { hasSupabasePublicEnv, normalizeInternalRedirectPath } from "@/lib/supabase/env";

export function SignupForm() {
  const router = useRouter();
  const params = useSearchParams();
  const redirect = normalizeInternalRedirectPath(params.get("redirect"));
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!hasSupabasePublicEnv()) {
    return (
      <p className="rounded-lg border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">
        Authentication is not configured. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in frontend/.env.local.
      </p>
    );
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);

    try {
      const supabase = createBrowserSupabaseClient();
      const callbackPath = `/auth/callback?next=${encodeURIComponent(redirect)}`;
      const configuredSiteUrl = (process.env.NEXT_PUBLIC_SITE_URL || "").trim();
      const emailRedirectTo =
        configuredSiteUrl
          ? `${configuredSiteUrl.replace(/\/+$/, "")}${callbackPath}`
          : typeof window !== "undefined"
            ? `${window.location.origin}${callbackPath}`
            : undefined;

      const { data, error: authError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo,
        },
      });

      if (authError) {
        if (authError.status === 429) {
          setError("Too many signup attempts. Please wait a minute and try again.");
          setLoading(false);
          return;
        }
        setError(authError.message);
        setLoading(false);
        return;
      }

      // If email confirmation is disabled, Supabase returns a session immediately.
      if (data.session) {
        // Give session cookies a moment to settle, then redirect
        setTimeout(() => {
          router.push(redirect);
        }, 300);
        return;
      }

      setMessage("Account created. Please check your inbox to confirm your email.");
      router.push(`/verify-email?email=${encodeURIComponent(email)}`);
    } catch (e: any) {
      console.error("Sign up error:", e);
      const errMsg = String(e?.message || e);
      if (errMsg.includes("Cannot convert undefined")) {
        setError("❌ Supabase not configured. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in Vercel env vars.");
      } else {
        setError(errMsg);
      }
      setLoading(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required placeholder="Email" className="w-full rounded-xl border border-stone-600 bg-stone-900 px-3 py-2" />
      <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required placeholder="Password" className="w-full rounded-xl border border-stone-600 bg-stone-900 px-3 py-2" />
      <button disabled={loading} className="w-full rounded-xl bg-amber-500 px-3 py-2 font-semibold text-stone-950 disabled:cursor-not-allowed disabled:opacity-60">
        {loading ? "Creating account..." : "Create Account"}
      </button>
      {message ? <p className="text-sm text-emerald-400">{message}</p> : null}
      {error ? <p className="text-sm text-red-400">{error}</p> : null}
    </form>
  );
}

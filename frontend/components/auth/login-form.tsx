"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { createBrowserSupabaseClient } from "@/lib/supabase/client";
import { hasSupabasePublicEnv, normalizeInternalRedirectPath } from "@/lib/supabase/env";

export function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const redirect = normalizeInternalRedirectPath(params.get("redirect"));
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
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
    setLoading(true);

    const supabase = createBrowserSupabaseClient();
    const { error: authError } = await supabase.auth.signInWithPassword({ email, password });

    setLoading(false);
    if (authError) {
      if (authError.status === 429) {
        setError("Too many sign-in attempts. Please wait a minute and try again.");
        return;
      }
      if (authError.message.toLowerCase().includes("email not confirmed")) {
        setError("This account is still marked unconfirmed. If you recently disabled email confirmation, create a new account or mark this user as confirmed in Supabase Auth users.");
        return;
      }
      setError(authError.message);
      return;
    }

    // Give session cookies a moment to settle, then redirect
    setTimeout(() => {
      router.push(redirect);
    }, 300);
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required placeholder="Email" className="w-full rounded-xl border border-stone-600 bg-stone-900 px-3 py-2" />
      <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required placeholder="Password" className="w-full rounded-xl border border-stone-600 bg-stone-900 px-3 py-2" />
      <button disabled={loading} className="w-full rounded-xl bg-amber-500 px-3 py-2 font-semibold text-stone-950">
        {loading ? "Signing in..." : "Sign In"}
      </button>
      {error ? <p className="text-sm text-red-400">{error}</p> : null}
    </form>
  );
}

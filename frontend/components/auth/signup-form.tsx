"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { createBrowserSupabaseClient } from "@/lib/supabase/client";

export function SignupForm() {
  const router = useRouter();
  const params = useSearchParams();
  const redirect = params.get("redirect") || "/dashboard";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);

    const supabase = createBrowserSupabaseClient();
    const { data, error: authError } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: typeof window !== "undefined" ? `${window.location.origin}${redirect}` : undefined,
      },
    });

    setLoading(false);

    if (authError) {
      if (authError.status === 429) {
        setError("Too many signup attempts. Please wait a minute and try again.");
        return;
      }
      setError(authError.message);
      return;
    }

    // If email confirmation is disabled, Supabase returns a session immediately.
    if (data.session) {
      router.replace(redirect);
      router.refresh();
      return;
    }

    setMessage("Account created. Please check your inbox to confirm your email.");
    router.push(`/verify-email?email=${encodeURIComponent(email)}`);
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

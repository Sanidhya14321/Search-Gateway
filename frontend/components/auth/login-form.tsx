"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { normalizeInternalRedirectPath } from "@/lib/auth/redirect";

export function LoginForm() {
  const router = useRouter();
  const { signIn } = useAuth();
  const params = useSearchParams();
  const redirect = normalizeInternalRedirectPath(params.get("redirect"));
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await signIn(email, password);

      // Give session cookies a moment to settle, then redirect
      setTimeout(() => {
        router.push(redirect);
      }, 300);
    } catch (e: any) {
      console.error("Sign in error:", e);
      setError(String(e?.message || e));
      setLoading(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required placeholder="Email" className="w-full rounded-xl border border-stone-300 bg-white px-3 py-2 text-stone-800" />
      <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required placeholder="Password" className="w-full rounded-xl border border-stone-300 bg-white px-3 py-2 text-stone-800" />
      <button disabled={loading} className="w-full rounded-xl bg-stone-900 px-3 py-2 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60">
        {loading ? "Signing in..." : "Sign In"}
      </button>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
    </form>
  );
}

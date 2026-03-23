"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { normalizeInternalRedirectPath } from "@/lib/auth/redirect";

export function SignupForm() {
  const router = useRouter();
  const { signUp } = useAuth();
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
      await signUp(email, password);
      setTimeout(() => {
        router.push(redirect);
      }, 300);
    } catch (e: any) {
      console.error("Sign up error:", e);
      setError(String(e?.message || e));
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
      {error ? <p className="text-sm text-red-400">{error}</p> : null}
    </form>
  );
}

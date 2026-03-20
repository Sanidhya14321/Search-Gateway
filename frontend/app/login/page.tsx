import Link from "next/link";
import { Suspense } from "react";
import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center px-6">
      <div className="w-full rounded-2xl border border-stone-700 bg-stone-900/80 p-6">
        <h1 className="mb-4 font-display text-3xl text-stone-100">Welcome back</h1>
        <Suspense fallback={<p className="text-sm text-stone-300">Loading login form...</p>}>
          <LoginForm />
        </Suspense>
        <p className="mt-4 text-sm text-stone-300">No account? <Link href="/signup" className="text-amber-300">Sign up</Link></p>
      </div>
    </main>
  );
}

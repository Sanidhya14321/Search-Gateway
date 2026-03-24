import Link from "next/link";
import { Suspense } from "react";
import { LoginForm } from "@/components/auth/login-form";
import { PublicNav } from "@/components/layout/public-nav";
import { PublicFooter } from "@/components/layout/public-footer";

export default function LoginPage() {
  return (
    <div className="page-wrap">
      <PublicNav />
      <main className="page-container grid gap-6 md:grid-cols-[1.1fr,0.9fr]">
        <section className="glass rounded-2xl p-6">
          <h1 className="font-display text-4xl text-stone-900">Welcome back</h1>
          <p className="mt-2 text-sm text-stone-600">Sign in to continue searching entities, running workflows, and reviewing citations.</p>
          <div className="mt-6">
            <Suspense fallback={<p className="text-sm text-stone-500">Loading login form...</p>}>
              <LoginForm />
            </Suspense>
          </div>
          <p className="mt-4 text-sm text-stone-600">
            No account? <Link href="/signup" className="font-medium text-teal-700 hover:text-teal-900">Sign up</Link>
          </p>
        </section>

        <aside className="glass rounded-2xl p-6">
          <h2 className="font-display text-2xl text-stone-900">Quick checklist</h2>
          <ul className="mt-3 space-y-2 text-sm text-stone-700">
            <li>Use the same email you used for signup.</li>
            <li>If login fails repeatedly, verify backend URL in diagnostics.</li>
            <li>After sign in, create API keys from settings for automation scripts.</li>
          </ul>
          <Link href="/diagnostics" className="mt-4 inline-flex rounded-lg border border-stone-300 px-3 py-2 text-sm text-stone-700 hover:border-stone-900 hover:text-stone-900">
            Open diagnostics
          </Link>
        </aside>
      </main>
      <PublicFooter />
    </div>
  );
}

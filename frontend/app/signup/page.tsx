import Link from "next/link";
import { Suspense } from "react";
import { SignupForm } from "@/components/auth/signup-form";
import { PublicNav } from "@/components/layout/public-nav";
import { PublicFooter } from "@/components/layout/public-footer";

export default function SignupPage() {
  return (
    <div className="page-wrap">
      <PublicNav />
      <main className="page-container grid gap-6 md:grid-cols-[1.1fr,0.9fr]">
        <section className="glass rounded-2xl p-6">
          <h1 className="font-display text-4xl text-stone-900">Create account</h1>
          <p className="mt-2 text-sm text-stone-600">Start with your organization email so your workspace history and API keys are tied to your team identity.</p>
          <div className="mt-6">
            <Suspense fallback={<p className="text-sm text-stone-500">Loading signup form...</p>}>
              <SignupForm />
            </Suspense>
          </div>
          <p className="mt-4 text-sm text-stone-600">
            Already have an account? <Link href="/login" className="font-medium text-teal-700 hover:text-teal-900">Sign in</Link>
          </p>
        </section>

        <aside className="glass rounded-2xl p-6">
          <h2 className="font-display text-2xl text-stone-900">What happens next</h2>
          <ul className="mt-3 space-y-2 text-sm text-stone-700">
            <li>Sign in and open Dashboard for quick actions.</li>
            <li>Run your first company or people search.</li>
            <li>Create API keys in settings to integrate from scripts.</li>
          </ul>
          <Link href="/features" className="mt-4 inline-flex rounded-lg border border-stone-300 px-3 py-2 text-sm text-stone-700 hover:border-stone-900 hover:text-stone-900">
            Explore features
          </Link>
        </aside>
      </main>
      <PublicFooter />
    </div>
  );
}

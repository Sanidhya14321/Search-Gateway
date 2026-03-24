import Link from "next/link";
import { PublicFooter } from "@/components/layout/public-footer";
import { PublicNav } from "@/components/layout/public-nav";

export default function ForgotPasswordPage() {
  return (
    <div className="page-wrap">
      <PublicNav />
      <main className="page-container max-w-3xl">
        <section className="glass rounded-2xl p-6">
          <h1 className="font-display text-3xl text-stone-900">Password reset</h1>
          <p className="mt-3 text-sm text-stone-700">
            Email-based password reset is not enabled in local auth mode yet. If you can still sign in, update credentials from your profile page.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link href="/login" className="rounded-lg bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800">
              Back to login
            </Link>
            <Link href="/profile" className="rounded-lg border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-700 hover:border-stone-900 hover:text-stone-900">
              Go to profile
            </Link>
          </div>
        </section>
      </main>
      <PublicFooter />
    </div>
  );
}

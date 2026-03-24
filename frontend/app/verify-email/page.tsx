import Link from "next/link";
import { PublicFooter } from "@/components/layout/public-footer";
import { PublicNav } from "@/components/layout/public-nav";

export default function VerifyEmailPage({
  searchParams,
}: {
  searchParams?: { email?: string };
}) {
  const email = searchParams?.email;

  return (
    <div className="page-wrap">
      <PublicNav />
      <main className="page-container max-w-3xl">
        <section className="glass rounded-2xl p-6">
          <h1 className="mb-3 font-display text-3xl text-stone-900">Verify your email</h1>
          <p className="text-stone-700">
            {email ? `We sent a confirmation link to ${email}.` : "We sent a confirmation link to your email address."}
          </p>
          <p className="mt-3 text-sm text-stone-600">
            In local auth mode, email verification is optional. If your account was created successfully, you can return and sign in now.
          </p>
          <Link href="/login" className="mt-6 inline-block rounded-lg bg-stone-900 px-4 py-2 font-medium text-white hover:bg-stone-800">
            Back to login
          </Link>
        </section>
      </main>
      <PublicFooter />
    </div>
  );
}

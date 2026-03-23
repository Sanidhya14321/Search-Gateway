import Link from "next/link";

export default function VerifyEmailPage({
  searchParams,
}: {
  searchParams?: { email?: string };
}) {
  const email = searchParams?.email;

  return (
    <main className="mx-auto max-w-md px-6 py-16 text-stone-100">
      <h1 className="mb-3 text-2xl font-semibold">Verify your email</h1>
      <p className="text-stone-300">
        {email ? `We sent a confirmation link to ${email}.` : "We sent a confirmation link to your email address."}
      </p>
      <p className="mt-3 text-sm text-stone-400">
        Email verification is optional in local auth mode. If you already created your account, go back and sign in.
      </p>
      <Link href="/login" className="mt-6 inline-block rounded-lg bg-amber-500 px-4 py-2 font-medium text-stone-900">
        Back to login
      </Link>
    </main>
  );
}

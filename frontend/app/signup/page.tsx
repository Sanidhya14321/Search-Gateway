import Link from "next/link";
import { SignupForm } from "@/components/auth/signup-form";

export default function SignupPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center px-6">
      <div className="w-full rounded-2xl border border-stone-700 bg-stone-900/80 p-6">
        <h1 className="mb-4 font-display text-3xl text-stone-100">Create account</h1>
        <SignupForm />
        <p className="mt-4 text-sm text-stone-300">Already have an account? <Link href="/login" className="text-amber-300">Sign in</Link></p>
      </div>
    </main>
  );
}

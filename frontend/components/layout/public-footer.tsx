import Link from "next/link";

export function PublicFooter() {
  return (
    <footer className="mt-16 border-t border-stone-300/70 bg-[color:var(--color-surface-2)]">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-10 md:grid-cols-3">
        <div>
          <h3 className="font-display text-xl font-semibold text-teal-900">CRMind</h3>
          <p className="mt-2 text-sm text-stone-600">
            Entity-first CRM intelligence platform with citation-grounded retrieval, signal tracking, and agent workflows.
          </p>
        </div>
        <div>
          <h4 className="text-sm font-semibold uppercase tracking-wide text-stone-500">Explore</h4>
          <div className="mt-2 space-y-1 text-sm text-stone-700">
            <p><Link href="/features">Features</Link></p>
            <p><Link href="/pricing">Pricing</Link></p>
            <p><Link href="/diagnostics">Diagnostics</Link></p>
          </div>
        </div>
        <div>
          <h4 className="text-sm font-semibold uppercase tracking-wide text-stone-500">Use</h4>
          <div className="mt-2 space-y-1 text-sm text-stone-700">
            <p><Link href="/login">Sign in</Link></p>
            <p><Link href="/signup">Create account</Link></p>
            <p><Link href="/contact">Support</Link></p>
          </div>
        </div>
      </div>
      <div className="border-t border-stone-300/70 px-4 py-4 text-center text-xs text-stone-500">
        © {new Date().getFullYear()} CRMind. Built for interviewers, managers, and technical leadership teams.
      </div>
    </footer>
  );
}

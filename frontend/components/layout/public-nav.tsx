import Link from "next/link";

const LINKS = [
  ["/", "Home"],
  ["/about", "About"],
  ["/features", "Features"],
  ["/pricing", "Pricing"],
  ["/diagnostics", "Diagnostics"],
  ["/contact", "Contact"],
];

export function PublicNav() {
  return (
    <header className="sticky top-0 z-50 border-b border-stone-300/60 bg-[color:var(--color-surface)]/90 backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="font-display text-xl font-semibold text-teal-900">
          CRMind
        </Link>
        <nav className="hidden items-center gap-4 text-sm text-stone-700 md:flex">
          {LINKS.map(([href, label]) => (
            <Link key={href} href={href} className="rounded-full px-3 py-1.5 transition hover:bg-teal-50 hover:text-teal-900">
              {label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <Link href="/login" className="rounded-full border border-stone-300 px-3 py-1.5 text-sm text-stone-700">
            Login
          </Link>
          <Link href="/signup" className="rounded-full bg-teal-700 px-3 py-1.5 text-sm font-semibold text-white">
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
}

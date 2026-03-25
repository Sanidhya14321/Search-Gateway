"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ThemeToggle } from "@/components/common/theme-toggle";
import { useAuth } from "@/context/auth-context";

const LINKS = [
  ["/dashboard", "Dashboard"],
  ["/search", "Search"],
  ["/agent", "Agent"],
  ["/signals", "Signals"],
  ["/history", "History"],
  ["/saved", "Saved"],
  ["/enrich", "Enrich"],
  ["/profile", "Profile"],
  ["/settings/api-keys", "Settings"],
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { signOut } = useAuth();

  return (
    <div className="page-wrap text-stone-900">
      <header className="sticky top-0 z-40 border-b border-stone-300/60 bg-[color:var(--color-surface)]/90 backdrop-blur">
        <div className="mx-auto flex w-full max-w-7xl flex-wrap items-center gap-3 px-4 py-3">
          <Link href="/dashboard" className="font-display text-xl font-semibold text-teal-900">
            CRMind
          </Link>
          <nav className="flex flex-1 flex-wrap items-center gap-2 text-sm">
            {LINKS.map(([href, label]) => (
              <Link
                key={href}
                href={href}
                className={`rounded-full px-3 py-1.5 transition ${pathname.startsWith(href) ? "bg-stone-900 text-white" : "text-stone-700 hover:bg-teal-50 hover:text-teal-900"}`}
              >
                {label}
              </Link>
            ))}
          </nav>
          <ThemeToggle />
          <button
            onClick={() => signOut()}
            className="rounded-full border border-stone-300 bg-white px-3 py-1.5 text-sm text-stone-700 hover:border-stone-900 hover:text-stone-900"
          >
            Sign out
          </button>
        </div>
      </header>
      <div className="mx-auto w-full max-w-7xl px-4 py-6">
        <section className="space-y-6">{children}</section>
      </div>
    </div>
  );
}

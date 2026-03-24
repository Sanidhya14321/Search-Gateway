"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
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
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-4 py-6 md:grid-cols-[260px,1fr]">
        <aside className="glass sticky top-4 h-fit rounded-2xl p-4">
          <h2 className="mb-1 font-display text-xl">CRMind</h2>
          <p className="mb-4 text-xs text-stone-500">Entity-first CRM intelligence workspace</p>
          <nav className="space-y-1">
            {LINKS.map(([href, label]) => (
              <Link
                key={href}
                href={href}
                className={`block rounded-lg px-3 py-2 text-sm transition ${pathname.startsWith(href) ? "bg-stone-900 text-stone-100" : "text-stone-600 hover:bg-white/70 hover:text-stone-900"}`}
              >
                {label}
              </Link>
            ))}
          </nav>
          <button
            onClick={() => signOut()}
            className="mt-6 w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-stone-700 hover:border-stone-900 hover:text-stone-900"
          >
            Sign out
          </button>
        </aside>
        <section className="space-y-6">{children}</section>
      </div>
    </div>
  );
}

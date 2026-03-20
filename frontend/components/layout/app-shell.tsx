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
    <div className="min-h-screen bg-stone-950 text-stone-100">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-4 py-6 md:grid-cols-[240px,1fr]">
        <aside className="rounded-2xl border border-stone-700 bg-stone-900/70 p-4">
          <h2 className="mb-4 font-display text-xl">CRMind</h2>
          <nav className="space-y-1">
            {LINKS.map(([href, label]) => (
              <Link
                key={href}
                href={href}
                className={`block rounded-lg px-3 py-2 text-sm ${pathname.startsWith(href) ? "bg-amber-500 text-stone-950" : "text-stone-300 hover:bg-stone-800"}`}
              >
                {label}
              </Link>
            ))}
          </nav>
          <button onClick={() => signOut()} className="mt-6 w-full rounded-lg border border-stone-600 px-3 py-2 text-sm text-stone-200">
            Sign out
          </button>
        </aside>
        <section>{children}</section>
      </div>
    </div>
  );
}

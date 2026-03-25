"use client";

import { useTheme } from "next-themes";

export function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const activeTheme = theme === "system" ? resolvedTheme : theme;
  const isDark = activeTheme === "dark";

  return (
    <button
      type="button"
      onClick={() => setTheme(isDark ? "light" : "dark")}
      className="rounded-full border border-[color:var(--color-border)] bg-[color:var(--color-surface)] px-3 py-1.5 text-sm text-[color:var(--color-text)] hover:border-[color:var(--color-border-strong)]"
      aria-label="Toggle theme"
      title="Toggle theme"
    >
      {isDark ? "Light" : "Dark"}
    </button>
  );
}

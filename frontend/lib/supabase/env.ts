type SupabasePublicEnv = {
  url: string;
  anonKey: string;
};

function clean(value: string | undefined): string {
  return (value ?? "").trim();
}

export function getSupabasePublicEnv(): SupabasePublicEnv {
  const url = clean(process.env.NEXT_PUBLIC_SUPABASE_URL);
  const anonKey = clean(process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);

  if (!url || !anonKey) {
    throw new Error(
      "Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY. " +
        "Set them in frontend/.env.local before using auth.",
    );
  }

  return { url, anonKey };
}

export function hasSupabasePublicEnv(): boolean {
  const url = clean(process.env.NEXT_PUBLIC_SUPABASE_URL);
  const anonKey = clean(process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);
  return Boolean(url && anonKey);
}

export function normalizeInternalRedirectPath(path: string | null | undefined): string {
  if (!path) {
    return "/dashboard";
  }

  const trimmed = path.trim();
  if (!trimmed.startsWith("/")) {
    return "/dashboard";
  }
  if (trimmed.startsWith("//")) {
    return "/dashboard";
  }
  if (trimmed.startsWith("/auth/callback")) {
    return "/dashboard";
  }

  return trimmed;
}

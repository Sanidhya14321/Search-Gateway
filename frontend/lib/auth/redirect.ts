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

import { createBrowserSupabaseClient } from "@/lib/supabase/client";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/+$/, "");

function buildApiUrl(path: string) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const hasVersionPrefix = API_BASE_URL.endsWith("/api/v1");
  const pathHasApiPrefix = normalizedPath.startsWith("/api/");

  if (hasVersionPrefix || pathHasApiPrefix) {
    return `${API_BASE_URL}${normalizedPath}`;
  }
  return `${API_BASE_URL}/api/v1${normalizedPath}`;
}

async function authHeaders() {
  const supabase = createBrowserSupabaseClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    throw new Error("No active session. Please log in.");
  }

  return {
    Authorization: `Bearer ${session.access_token}`,
    "Content-Type": "application/json",
  };
}

async function parseResponse(response: Response) {
  if (response.ok) {
    return response.json();
  }

  const text = await response.text();
  throw new Error(text || `HTTP ${response.status}`);
}

export async function apiGet(path: string) {
  const headers = await authHeaders();
  const response = await fetch(buildApiUrl(path), {
    method: "GET",
    headers,
    cache: "no-store",
  });
  return parseResponse(response);
}

export async function apiPost(path: string, body: unknown) {
  const headers = await authHeaders();
  const response = await fetch(buildApiUrl(path), {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  return parseResponse(response);
}

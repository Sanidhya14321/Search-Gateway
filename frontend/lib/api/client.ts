const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/+$/, "");
const USE_BROWSER_PROXY = process.env.NEXT_PUBLIC_USE_API_PROXY !== "false";
const ACCESS_TOKEN_KEY = "crmind_access_token";

export function buildApiUrl(path: string) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;

  // Browser requests default to same-origin proxy to eliminate CORS issues.
  if (typeof window !== "undefined" && USE_BROWSER_PROXY) {
    if (normalizedPath.startsWith("/api/")) {
      return `/api/proxy${normalizedPath}`;
    }
    return `/api/proxy/api/v1${normalizedPath}`;
  }

  const baseHasVersionPrefix = API_BASE_URL.endsWith("/api/v1");

  if (baseHasVersionPrefix) {
    if (normalizedPath === "/api/v1") {
      return API_BASE_URL;
    }
    if (normalizedPath.startsWith("/api/v1/")) {
      return `${API_BASE_URL}${normalizedPath.slice("/api/v1".length)}`;
    }
    return `${API_BASE_URL}${normalizedPath}`;
  }

  if (normalizedPath.startsWith("/api/")) {
    return `${API_BASE_URL}${normalizedPath}`;
  }

  return `${API_BASE_URL}/api/v1${normalizedPath}`;
}

function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setAccessToken(token: string | null) {
  if (typeof window === "undefined") {
    return;
  }
  if (!token) {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    return;
  }
  window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
}

export function clearAccessToken() {
  setAccessToken(null);
}

async function authHeaders() {
  const accessToken = getAccessToken();
  if (!accessToken) {
    throw new Error("No active session. Please log in.");
  }

  return {
    Authorization: `Bearer ${accessToken}`,
    "Content-Type": "application/json",
  };
}

async function apiRequest(path: string, init: RequestInit = {}) {
  const headers = await authHeaders();
  const response = await fetch(buildApiUrl(path), {
    ...init,
    headers: {
      ...headers,
      ...(init.headers || {}),
    },
    cache: init.cache ?? "no-store",
  });
  return parseResponse(response);
}

async function parseResponse(response: Response) {
  if (response.ok) {
    return response.json();
  }

  const text = await response.text();
  let detail: string | null = null;
  try {
    const parsed = JSON.parse(text);
    detail = parsed?.detail || parsed?.message || parsed?.error || null;
  } catch {
    // Fall through to plain text error handling.
  }
  if (detail) {
    throw new Error(String(detail));
  }
  throw new Error(text || `HTTP ${response.status}`);
}

export async function apiGet(path: string) {
  return apiRequest(path, { method: "GET" });
}

export async function apiPost(path: string, body: unknown) {
  return apiRequest(path, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function apiDelete(path: string) {
  return apiRequest(path, { method: "DELETE" });
}

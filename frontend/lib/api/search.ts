import { apiGet, apiPost } from "@/lib/api/client";

export function searchEntities(query: string) {
  return apiGet(`/api/v1/search?q=${encodeURIComponent(query)}`);
}

export function runSearch(query: string) {
  return apiPost("/api/v1/search", { query });
}

import { apiGet } from "@/lib/api/client";

export function getAccountBrief(id: string) {
  return apiGet(`/api/v1/account/${id}/brief`);
}

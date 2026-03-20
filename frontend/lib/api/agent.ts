import { apiPost } from "@/lib/api/client";

export function runAgent(workflowName: string, query: string) {
  return apiPost("/api/v1/agent/run", { workflow_name: workflowName, query });
}

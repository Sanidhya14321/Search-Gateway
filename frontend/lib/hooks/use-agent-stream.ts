"use client";

import { useEffect, useRef, useState } from "react";

export type StreamEvent = {
  type: string;
  payload: unknown;
};

export function useAgentStream(runId: string | null) {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!runId) return;

    const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
    const source = new EventSource(`${base}/api/v1/agent/stream/${runId}`);
    sourceRef.current = source;

    source.onopen = () => setConnected(true);
    source.onerror = () => setConnected(false);
    source.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setEvents((prev) => [...prev, parsed]);
      } catch {
        setEvents((prev) => [...prev, { type: "message", payload: event.data }]);
      }
    };

    return () => {
      source.close();
      sourceRef.current = null;
      setConnected(false);
    };
  }, [runId]);

  return { events, connected };
}

type Signal = {
  signal_type?: string;
  description?: string;
  confidence?: number;
  detected_at?: string;
};

export function SignalTimeline({ signals }: { signals: Signal[] }) {
  return (
    <ul className="space-y-3">
      {signals.map((signal, idx) => (
        <li key={`${signal.signal_type}-${idx}`} className="rounded-xl border border-stone-200 bg-white/80 p-4">
          <p className="text-xs uppercase tracking-wide text-teal-700">{signal.signal_type || "signal"}</p>
          <p className="mt-1 text-sm text-stone-700">{signal.description || "No description"}</p>
          <p className="mt-2 text-xs text-stone-500">confidence {(signal.confidence ?? 0).toFixed(2)} • {signal.detected_at || "n/a"}</p>
        </li>
      ))}
    </ul>
  );
}

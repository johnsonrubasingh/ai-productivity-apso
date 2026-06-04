type ResultPanelProps = {
  title: string;
  result: unknown;
};

export function ResultPanel({ title, result }: ResultPanelProps) {
  return (
    <div className="rounded-lg border border-[var(--border)] bg-white">
      <div className="border-b border-[var(--border)] px-5 py-4">
        <h3 className="text-sm font-semibold">{title}</h3>
      </div>
      <pre className="max-h-[32rem] overflow-auto p-5 font-mono text-xs leading-6 text-slate-700">
        {result ? JSON.stringify(result, null, 2) : "No response yet."}
      </pre>
    </div>
  );
}

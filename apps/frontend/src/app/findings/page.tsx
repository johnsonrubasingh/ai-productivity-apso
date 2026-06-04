import { AppShell } from "@/components/shell";
import { StatusPill } from "@/components/status-pill";
import { getDashboardData } from "@/lib/api";
import type { Finding } from "@/lib/types";

const severityTone: Record<Finding["severity"], "danger" | "warning" | "neutral"> = {
  critical: "danger",
  high: "danger",
  medium: "warning",
  low: "neutral",
};

export default async function FindingsPage() {
  const data = await getDashboardData();

  return (
    <AppShell>
      <div className="mx-auto max-w-7xl rounded-lg border border-[var(--border)] bg-white">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)] px-5 py-4">
          <div>
            <h2 className="text-base font-semibold">Findings Triage</h2>
            <p className="text-sm text-[var(--muted)]">Central queue for AI and scanner findings from APSO backend.</p>
          </div>
          <StatusPill label={`${data.findings.length} visible`} tone="accent" />
        </div>
        <div className="grid gap-4 p-5 lg:grid-cols-3">
          {data.findings.map((finding) => (
            <article className="rounded-lg border border-[var(--border)] bg-slate-50 p-4" key={finding.id}>
              <div className="flex flex-wrap items-center gap-2">
                <StatusPill label={finding.severity} tone={severityTone[finding.severity]} />
                <StatusPill label={finding.status} />
              </div>
              <h3 className="mt-3 text-sm font-semibold text-slate-950">{finding.title}</h3>
              <p className="mt-2 text-sm text-slate-700">{finding.evidence}</p>
              <div className="mt-4 grid gap-2 text-xs font-semibold text-slate-600">
                <div>Source: {finding.source}</div>
                <div>Owner: {finding.owner}</div>
                <div className="font-mono">{finding.id}</div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </AppShell>
  );
}

import type { DashboardData, Finding, ReadinessSignal } from "@/lib/types";
import { StatusPill } from "./status-pill";

const severityTone: Record<Finding["severity"], "danger" | "warning" | "neutral"> = {
  critical: "danger",
  high: "danger",
  medium: "warning",
  low: "neutral",
};

const readinessTone: Record<ReadinessSignal["status"], "success" | "warning" | "danger"> = {
  pass: "success",
  watch: "warning",
  block: "danger",
};

export function DashboardSections({ data }: { data: DashboardData }) {
  const openFindings = data.findings.filter((finding) => finding.status !== "resolved").length;
  const blockedSignals = data.readiness.filter((signal) => signal.status === "block").length;

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <section className="rounded-lg border border-[var(--border)] bg-white px-5 py-4">
        <div className="grid gap-4 lg:grid-cols-[1fr_auto]">
          <div>
            <h2 className="text-base font-semibold">APSO Implementation Flow</h2>
            <p className="text-sm text-[var(--muted)]">
              Configure records, ingest read-only source data, inspect evidence, then run AI analysis.
            </p>
          </div>
          <div className="grid gap-2 sm:grid-cols-4">
            <ActionLink href="/setup" label="Setup" />
            <ActionLink href="/ingestion" label="Ingest" />
            <ActionLink href="/explorer" label="Explore" />
            <ActionLink href="/workbench" label="Analyze" />
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Metric label="Active findings" value={String(openFindings)} detail="Open or triaged" />
        <Metric label="AI engines" value={String(data.engines.length)} detail="Gateway routed" />
        <Metric label="Integrations" value={String(data.integrations.length)} detail="Configurable" />
        <Metric label="Blocked signals" value={String(blockedSignals)} detail="Release gates" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]" id="dashboard">
        <div className="rounded-lg border border-[var(--border)] bg-white">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)] px-5 py-4">
            <div>
              <h2 className="text-base font-semibold">Findings Inbox</h2>
              <p className="text-sm text-[var(--muted)]">AI findings from requirements, code, coverage, and release checks.</p>
            </div>
            <StatusPill label="Backend API ready" tone="accent" />
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-5 py-3 font-semibold">Finding</th>
                  <th className="px-5 py-3 font-semibold">Severity</th>
                  <th className="px-5 py-3 font-semibold">Source</th>
                  <th className="px-5 py-3 font-semibold">Owner</th>
                  <th className="px-5 py-3 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody>
                {data.findings.map((finding) => (
                  <tr className="border-t border-[var(--border)]" key={finding.id}>
                    <td className="max-w-md px-5 py-4 align-top">
                      <div className="font-semibold text-slate-900">{finding.title}</div>
                      <div className="mt-1 text-xs text-[var(--muted)]">{finding.evidence}</div>
                    </td>
                    <td className="px-5 py-4 align-top">
                      <StatusPill label={finding.severity} tone={severityTone[finding.severity]} />
                    </td>
                    <td className="px-5 py-4 align-top text-slate-700">{finding.source}</td>
                    <td className="px-5 py-4 align-top text-slate-700">{finding.owner}</td>
                    <td className="px-5 py-4 align-top">
                      <StatusPill label={finding.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-lg border border-[var(--border)] bg-white" id="release">
          <div className="border-b border-[var(--border)] px-5 py-4">
            <h2 className="text-base font-semibold">Release Readiness</h2>
            <p className="text-sm text-[var(--muted)]">Current gate posture based on available APSO signals.</p>
          </div>
          <div className="space-y-4 p-5">
            {data.readiness.map((signal) => (
              <div key={signal.name}>
                <div className="mb-2 flex items-center justify-between gap-3">
                  <span className="text-sm font-semibold">{signal.name}</span>
                  <StatusPill label={`${signal.score}% ${signal.status}`} tone={readinessTone[signal.status]} />
                </div>
                <div className="h-2 rounded-full bg-slate-100">
                  <div
                    className="h-2 rounded-full bg-[var(--accent)]"
                    style={{ width: `${Math.max(4, Math.min(signal.score, 100))}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2" id="integrations">
        <div className="rounded-lg border border-[var(--border)] bg-white">
          <div className="border-b border-[var(--border)] px-5 py-4">
            <h2 className="text-base font-semibold">Integration Registry</h2>
            <p className="text-sm text-[var(--muted)]">Read-only extraction and mock boundaries are locked for MVP.</p>
          </div>
          <div className="divide-y divide-[var(--border)]">
            {data.integrations.map((integration) => (
              <div className="grid gap-3 px-5 py-4 sm:grid-cols-[1fr_auto]" key={integration.id}>
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-sm font-semibold">{integration.name}</h3>
                    <StatusPill label={integration.mode} tone={integration.mode === "mock" ? "warning" : "accent"} />
                    <StatusPill label={integration.state} />
                  </div>
                  <p className="mt-2 text-sm text-slate-700">{integration.notes}</p>
                  <p className="mt-1 font-mono text-xs text-[var(--muted)]">{integration.scope}</p>
                </div>
                <div className="text-sm font-medium text-[var(--muted)]">{integration.lastChecked}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-[var(--border)] bg-white" id="ai-engines">
          <div className="border-b border-[var(--border)] px-5 py-4">
            <h2 className="text-base font-semibold">AI Engine Map</h2>
            <p className="text-sm text-[var(--muted)]">Every engine routes through the APSO AI Gateway.</p>
          </div>
          <div className="divide-y divide-[var(--border)]">
            {data.engines.map((engine) => (
              <div className="px-5 py-4" key={engine.id}>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h3 className="text-sm font-semibold">{engine.name}</h3>
                  <StatusPill label={engine.state} tone="success" />
                </div>
                <p className="mt-2 text-sm text-slate-700">{engine.signal}</p>
                <div className="mt-3 rounded-md bg-slate-50 px-3 py-2 font-mono text-xs text-slate-600">
                  {engine.route}
                </div>
                <p className="mt-2 text-xs font-medium text-[var(--muted)]">{engine.coverage}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-[var(--border)] bg-white" id="findings">
        <div className="grid gap-4 px-5 py-4 md:grid-cols-[0.8fr_1.2fr]">
          <div>
            <h2 className="text-base font-semibold">Proof Pack Assembly</h2>
            <p className="mt-1 text-sm text-[var(--muted)]">
              Evidence package generated from work items, code analysis, coverage checks, and release gates.
            </p>
          </div>
          <div className="grid gap-2 sm:grid-cols-2">
            {data.proofPackItems.map((item) => (
              <div className="rounded-md border border-[var(--border)] bg-slate-50 px-3 py-2 text-sm font-medium" key={item}>
                {item}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

function Metric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="rounded-lg border border-[var(--border)] bg-white px-5 py-4">
      <div className="text-sm font-medium text-[var(--muted)]">{label}</div>
      <div className="mt-2 text-3xl font-semibold tracking-[0]">{value}</div>
      <div className="mt-1 text-xs font-semibold uppercase text-slate-500">{detail}</div>
    </div>
  );
}

function ActionLink({ href, label }: { href: string; label: string }) {
  return (
    <a
      className="focus-ring flex h-10 items-center justify-center rounded-md border border-[var(--border)] bg-white px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50"
      href={href}
    >
      {label}
    </a>
  );
}

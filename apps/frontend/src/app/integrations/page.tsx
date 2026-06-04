import { IntegrationChecks } from "@/components/integration-checks";
import { AppShell } from "@/components/shell";
import { StatusPill } from "@/components/status-pill";
import { getDashboardData } from "@/lib/api";

export default async function IntegrationsPage() {
  const data = await getDashboardData();

  return (
    <AppShell>
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="rounded-lg border border-[var(--border)] bg-white">
          <div className="border-b border-[var(--border)] px-5 py-4">
            <h2 className="text-base font-semibold">Configured Integrations</h2>
            <p className="text-sm text-[var(--muted)]">MVP scope stays extraction-only for Jira and Bitbucket.</p>
          </div>
          <div className="grid gap-4 p-5 md:grid-cols-2">
            {data.integrations.map((integration) => (
              <article className="rounded-lg border border-[var(--border)] bg-slate-50 p-4" key={integration.id}>
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-sm font-semibold">{integration.name}</h3>
                  <StatusPill label={integration.mode} tone={integration.mode === "mock" ? "warning" : "accent"} />
                  <StatusPill label={integration.state} />
                </div>
                <p className="mt-3 text-sm text-slate-700">{integration.notes}</p>
                <div className="mt-3 rounded-md bg-white px-3 py-2 font-mono text-xs text-slate-600">
                  {integration.scope}
                </div>
              </article>
            ))}
          </div>
        </section>

        <IntegrationChecks />
      </div>
    </AppShell>
  );
}

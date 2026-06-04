import Link from "next/link";
import { AppShell } from "@/components/shell";

const routes = [
  "GET /api/v1/health",
  "GET /api/v1/integrations",
  "GET /api/v1/ai/tasks",
  "POST /api/v1/engines/definition-gap/analyze",
  "POST /api/v1/engines/code-quality/analyze",
  "POST /api/v1/engines/coverage/verify",
  "POST /api/v1/quality/release-readiness",
  "POST /api/v1/reports/proof-pack",
  "GET /api/v1/findings",
];

export default function ApiContractPage() {
  return (
    <AppShell>
      <div className="mx-auto max-w-5xl rounded-lg border border-[var(--border)] bg-white">
        <div className="border-b border-[var(--border)] px-5 py-4">
          <Link className="focus-ring text-sm font-semibold text-[var(--accent)]" href="/">
            Back to dashboard
          </Link>
          <h2 className="mt-3 text-lg font-semibold">Backend Contract Surface</h2>
          <p className="mt-1 text-sm text-[var(--muted)]">
            Frontend integration points currently mapped to the FastAPI backend.
          </p>
        </div>
        <div className="grid gap-2 p-5 sm:grid-cols-2">
          {routes.map((route) => (
            <div className="rounded-md border border-[var(--border)] bg-slate-50 px-3 py-2 font-mono text-xs" key={route}>
              {route}
            </div>
          ))}
        </div>
      </div>
    </AppShell>
  );
}

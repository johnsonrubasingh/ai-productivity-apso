"use client";

import { useState } from "react";
import { getBackend } from "@/lib/client-api";
import { ResultPanel } from "./result-panel";

const checks = [
  { label: "Jira connection", path: "/integrations/jira/check" },
  { label: "Bitbucket connection", path: "/integrations/bitbucket/check" },
  { label: "AI provider health", path: "/ai/provider/health" },
  { label: "Runtime readiness", path: "/ops/readiness" },
];

export function IntegrationChecks() {
  const [result, setResult] = useState<unknown>(null);
  const [activePath, setActivePath] = useState<string | null>(null);

  async function runCheck(path: string) {
    setActivePath(path);
    setResult(await getBackend(path));
    setActivePath(null);
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
      <section className="rounded-lg border border-[var(--border)] bg-white">
        <div className="border-b border-[var(--border)] px-5 py-4">
          <h2 className="text-base font-semibold">Live Checks</h2>
          <p className="text-sm text-[var(--muted)]">Validate configured services from the browser against backend endpoints.</p>
        </div>
        <div className="space-y-3 p-5">
          {checks.map((check) => (
            <button
              className="focus-ring flex min-h-12 w-full items-center justify-between gap-3 rounded-md border border-[var(--border)] bg-white px-4 py-3 text-left text-sm font-semibold hover:bg-slate-50 disabled:cursor-not-allowed disabled:bg-slate-100"
              disabled={activePath !== null}
              key={check.path}
              onClick={() => void runCheck(check.path)}
              type="button"
            >
              <span>{check.label}</span>
              <span className="font-mono text-xs text-[var(--muted)]">
                {activePath === check.path ? "running" : check.path}
              </span>
            </button>
          ))}
        </div>
      </section>
      <ResultPanel result={result} title="Check Response" />
    </div>
  );
}

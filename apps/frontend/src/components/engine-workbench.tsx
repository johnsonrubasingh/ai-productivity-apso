"use client";

import { useMemo, useState } from "react";
import { postBackend } from "@/lib/client-api";
import { ResultPanel } from "./result-panel";
import { StatusPill } from "./status-pill";

type EngineId = "definition" | "code" | "coverage" | "release" | "proof";

const engineTabs: { id: EngineId; label: string }[] = [
  { id: "definition", label: "Definition Gap" },
  { id: "code", label: "Code Quality" },
  { id: "coverage", label: "Coverage" },
  { id: "release", label: "Release" },
  { id: "proof", label: "Proof Pack" },
];

const samplePayloads: Record<EngineId, string> = {
  definition: JSON.stringify(
    {
      tenant_id: "default",
      project_id: "apso-dev",
      issue_key: "APSO-101",
      summary: "As a release manager, I need AI readiness evidence before production approval.",
      description: "The system should detect missing acceptance criteria, code risk, and coverage gaps.",
      acceptance_criteria: "Given release evidence exists, when readiness is checked, then blockers are listed.",
      comments: ["MVP must stay read-only for Jira and Bitbucket."],
    },
    null,
    2,
  ),
  code: JSON.stringify(
    {
      repository_slug: "or-pems-plt-sandbox-api",
      branch: "develop",
      scanners: ["semgrep", "gitleaks", "trivy"],
      repository_path: null,
      execute_scanners: false,
    },
    null,
    2,
  ),
  coverage: JSON.stringify(
    {
      work_item_key: "APSO-101",
      linked_commits: 2,
      linked_pull_requests: 1,
      linked_test_runs: 3,
      successful_pipeline_runs: 1,
      coverage_percent: 72,
    },
    null,
    2,
  ),
  release: JSON.stringify(
    {
      project_id: "apso-dev",
      release_name: "APSO MVP Backend + Frontend Foundation",
      open_high_risk_findings: 1,
      failed_pipeline_runs: 0,
      stories_without_tests: 2,
      unresolved_requirement_gaps: 1,
    },
    null,
    2,
  ),
  proof: JSON.stringify(
    {
      project_id: "apso-dev",
      title: "APSO AI Productivity Proof Pack",
      include_placeholders: true,
    },
    null,
    2,
  ),
};

const routes: Record<EngineId, { path: string; params?: Record<string, string | boolean> }> = {
  definition: {
    path: "/engines/definition-gap/analyze",
    params: { use_llm: false, persist: false },
  },
  code: { path: "/engines/code-quality/analyze" },
  coverage: { path: "/engines/coverage/verify" },
  release: { path: "/quality/release-readiness" },
  proof: { path: "/reports/proof-pack" },
};

export function EngineWorkbench() {
  const [activeEngine, setActiveEngine] = useState<EngineId>("definition");
  const [payloads, setPayloads] = useState(samplePayloads);
  const [result, setResult] = useState<unknown>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const activeRoute = useMemo(() => routes[activeEngine], [activeEngine]);

  async function runEngine() {
    setIsSubmitting(true);
    setResult(null);

    try {
      const parsed = JSON.parse(payloads[activeEngine]) as unknown;
      const response = await postBackend(activeRoute.path, parsed, activeRoute.params);
      setResult(response);
    } catch (error) {
      setResult({
        ok: false,
        error: error instanceof Error ? error.message : "Invalid JSON payload",
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="mx-auto grid max-w-7xl gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <section className="rounded-lg border border-[var(--border)] bg-white">
        <div className="border-b border-[var(--border)] px-5 py-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-semibold">Engine Workbench</h2>
              <p className="text-sm text-[var(--muted)]">Submit contract-valid payloads to the FastAPI backend.</p>
            </div>
            <StatusPill label="read-only safe" tone="accent" />
          </div>
        </div>

        <div className="border-b border-[var(--border)] p-3">
          <div className="grid gap-2 sm:grid-cols-5">
            {engineTabs.map((tab) => (
              <button
                className={`focus-ring h-10 rounded-md border px-3 text-sm font-semibold ${
                  activeEngine === tab.id
                    ? "border-[var(--accent)] bg-[var(--accent)] text-white"
                    : "border-[var(--border)] bg-white text-slate-700 hover:bg-slate-50"
                }`}
                key={tab.id}
                onClick={() => {
                  setActiveEngine(tab.id);
                  setResult(null);
                }}
                type="button"
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-4 p-5">
          <div>
            <label className="mb-2 block text-sm font-semibold" htmlFor="payload">
              Request payload
            </label>
            <textarea
              className="focus-ring min-h-96 w-full resize-y rounded-md border border-[var(--border)] bg-slate-50 p-3 font-mono text-xs leading-6 text-slate-800"
              id="payload"
              onChange={(event) =>
                setPayloads((current) => ({
                  ...current,
                  [activeEngine]: event.target.value,
                }))
              }
              spellCheck={false}
              value={payloads[activeEngine]}
            />
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="rounded-md bg-slate-50 px-3 py-2 font-mono text-xs text-slate-600">
              POST {activeRoute.path}
            </div>
            <button
              className="focus-ring h-10 rounded-md bg-[var(--accent)] px-4 text-sm font-semibold text-white hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-400"
              disabled={isSubmitting}
              onClick={runEngine}
              type="button"
            >
              {isSubmitting ? "Running..." : "Run"}
            </button>
          </div>
        </div>
      </section>

      <ResultPanel result={result} title="Backend Response" />
    </div>
  );
}

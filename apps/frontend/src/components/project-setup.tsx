"use client";

import { useState } from "react";
import { getBackend, postBackend } from "@/lib/client-api";
import { ResultPanel } from "./result-panel";

const defaultTenantPayload = JSON.stringify(
  {
    name: "APSO Development Tenant",
    slug: "apso-dev",
    timezone: "Asia/Calcutta",
  },
  null,
  2,
);

const defaultProjectPayload = JSON.stringify(
  {
    name: "APSO Productivity Platform",
    key: "APSO",
    description: "AI-powered SDLC productivity, quality, and release intelligence application.",
  },
  null,
  2,
);

export function ProjectSetup() {
  const [tenantPayload, setTenantPayload] = useState(defaultTenantPayload);
  const [projectPayload, setProjectPayload] = useState(defaultProjectPayload);
  const [result, setResult] = useState<unknown>(null);
  const [isBusy, setIsBusy] = useState(false);

  async function execute(action: () => Promise<unknown>) {
    setIsBusy(true);
    setResult(null);
    try {
      setResult(await action());
    } catch (error) {
      setResult({
        ok: false,
        error: error instanceof Error ? error.message : "Action failed",
      });
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <div className="mx-auto grid max-w-7xl gap-6 xl:grid-cols-[1fr_1fr]">
      <section className="space-y-6">
        <EditorCard
          buttonLabel="Create Tenant"
          disabled={isBusy}
          onChange={setTenantPayload}
          onSubmit={() =>
            execute(async () => postBackend("/core/tenants", JSON.parse(tenantPayload) as unknown))
          }
          payload={tenantPayload}
          title="Tenant"
        />

        <EditorCard
          buttonLabel="Create Project"
          disabled={isBusy}
          onChange={setProjectPayload}
          onSubmit={() =>
            execute(async () => postBackend("/core/projects", JSON.parse(projectPayload) as unknown))
          }
          payload={projectPayload}
          title="Project"
        />

        <div className="grid gap-3 sm:grid-cols-3">
          <ActionButton disabled={isBusy} label="List Tenants" onClick={() => execute(() => getBackend("/core/tenants"))} />
          <ActionButton disabled={isBusy} label="List Projects" onClick={() => execute(() => getBackend("/core/projects"))} />
          <ActionButton
            disabled={isBusy}
            label="List Work Items"
            onClick={() => execute(() => getBackend("/core/work-items?limit=50"))}
          />
        </div>
      </section>

      <ResultPanel result={result} title="Setup Response" />
    </div>
  );
}

function EditorCard({
  buttonLabel,
  disabled,
  onChange,
  onSubmit,
  payload,
  title,
}: {
  buttonLabel: string;
  disabled: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
  payload: string;
  title: string;
}) {
  return (
    <div className="rounded-lg border border-[var(--border)] bg-white">
      <div className="flex items-center justify-between gap-3 border-b border-[var(--border)] px-5 py-4">
        <h2 className="text-base font-semibold">{title}</h2>
        <button
          className="focus-ring h-10 rounded-md bg-[var(--accent)] px-4 text-sm font-semibold text-white hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          disabled={disabled}
          onClick={onSubmit}
          type="button"
        >
          {buttonLabel}
        </button>
      </div>
      <div className="p-5">
        <textarea
          className="focus-ring min-h-56 w-full resize-y rounded-md border border-[var(--border)] bg-slate-50 p-3 font-mono text-xs leading-6 text-slate-800"
          onChange={(event) => onChange(event.target.value)}
          spellCheck={false}
          value={payload}
        />
      </div>
    </div>
  );
}

function ActionButton({
  disabled,
  label,
  onClick,
}: {
  disabled: boolean;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      className="focus-ring h-11 rounded-md border border-[var(--border)] bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:bg-slate-100"
      disabled={disabled}
      onClick={onClick}
      type="button"
    >
      {label}
    </button>
  );
}

"use client";

import { useMemo, useState } from "react";
import { getBackend } from "@/lib/client-api";
import { ResultPanel } from "./result-panel";
import { StatusPill } from "./status-pill";

type WorkItem = {
  id: string;
  issue_key: string;
  issue_type: string;
  status: string;
  summary: string;
  source: string;
};

type Repository = {
  slug: string;
  name: string;
  full_name: string;
  main_branch?: string | null;
  source_url?: string | null;
};

type PullRequest = {
  id: number;
  title: string;
  state: string;
  author?: string | null;
  source_branch?: string | null;
  target_branch?: string | null;
};

type Commit = {
  hash: string;
  message?: string | null;
  author?: string | null;
  branch?: string | null;
  committed_at?: string | null;
};

type Pipeline = {
  uuid: string;
  state: string;
  result?: string | null;
  branch?: string | null;
  commit_sha?: string | null;
};

type Scanner = {
  name: string;
  purpose: string;
  enabled_for_mvp: boolean;
  requires_external_service: boolean;
};

type ExplorerTable =
  | { kind: "work-items"; rows: WorkItem[] }
  | { kind: "repositories"; rows: Repository[] }
  | { kind: "pull-requests"; rows: PullRequest[] }
  | { kind: "commits"; rows: Commit[] }
  | { kind: "pipelines"; rows: Pipeline[] }
  | { kind: "scanners"; rows: Scanner[] }
  | null;

export function EvidenceExplorer() {
  const [repoSlug, setRepoSlug] = useState("or-pems-plt-sandbox-api");
  const [result, setResult] = useState<unknown>(null);
  const [table, setTable] = useState<ExplorerTable>(null);
  const [isBusy, setIsBusy] = useState(false);

  const encodedRepoSlug = useMemo(() => encodeURIComponent(repoSlug), [repoSlug]);

  async function load<T>(path: string, extract: (data: T) => ExplorerTable) {
    setIsBusy(true);
    setResult(null);
    setTable(null);
    const response = await getBackend<T>(path);
    setResult(response);
    if (response.ok) {
      setTable(extract(response.data));
    }
    setIsBusy(false);
  }

  return (
    <div className="mx-auto grid max-w-7xl gap-6 xl:grid-cols-[1.05fr_0.95fr]">
      <section className="space-y-6">
        <div className="rounded-lg border border-[var(--border)] bg-white">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)] px-5 py-4">
            <div>
              <h2 className="text-base font-semibold">Evidence Sources</h2>
              <p className="text-sm text-[var(--muted)]">Inspect read-only and ingested records used by APSO engines.</p>
            </div>
            <StatusPill label="extract only" tone="accent" />
          </div>
          <div className="grid gap-3 p-5 sm:grid-cols-2 xl:grid-cols-3">
            <ActionButton
              disabled={isBusy}
              label="Work Items"
              onClick={() =>
                void load<WorkItem[]>("/core/work-items?limit=100", (rows) => ({
                  kind: "work-items",
                  rows,
                }))
              }
            />
            <ActionButton
              disabled={isBusy}
              label="Project Health"
              onClick={() => void load<Record<string, unknown>>("/dashboard/project-health", () => null)}
            />
            <ActionButton
              disabled={isBusy}
              label="Scanners"
              onClick={() =>
                void load<Scanner[]>("/quality/scanners", (rows) => ({
                  kind: "scanners",
                  rows,
                }))
              }
            />
            <ActionButton
              disabled={isBusy}
              label="Repositories"
              onClick={() =>
                void load<{ repositories: Repository[] }>("/integrations/bitbucket/repositories", (data) => ({
                  kind: "repositories",
                  rows: data.repositories,
                }))
              }
            />
          </div>
        </div>

        <div className="rounded-lg border border-[var(--border)] bg-white">
          <div className="border-b border-[var(--border)] px-5 py-4">
            <h2 className="text-base font-semibold">Repository Artifacts</h2>
            <p className="text-sm text-[var(--muted)]">Use a Bitbucket repository slug from the integration response.</p>
          </div>
          <div className="space-y-4 p-5">
            <label className="block">
              <span className="mb-2 block text-sm font-semibold">Repository slug</span>
              <input
                className="focus-ring h-11 w-full rounded-md border border-[var(--border)] bg-white px-3 text-sm"
                onChange={(event) => setRepoSlug(event.target.value)}
                value={repoSlug}
              />
            </label>
            <div className="grid gap-3 sm:grid-cols-3">
              <ActionButton
                disabled={isBusy}
                label="Pull Requests"
                onClick={() =>
                  void load<{ pull_requests: PullRequest[] }>(
                    `/integrations/bitbucket/repositories/${encodedRepoSlug}/pull-requests`,
                    (data) => ({
                      kind: "pull-requests",
                      rows: data.pull_requests,
                    }),
                  )
                }
              />
              <ActionButton
                disabled={isBusy}
                label="Commits"
                onClick={() =>
                  void load<{ commits: Commit[] }>(`/integrations/bitbucket/repositories/${encodedRepoSlug}/commits`, (data) => ({
                    kind: "commits",
                    rows: data.commits,
                  }))
                }
              />
              <ActionButton
                disabled={isBusy}
                label="Pipelines"
                onClick={() =>
                  void load<{ pipelines: Pipeline[] }>(
                    `/integrations/bitbucket/repositories/${encodedRepoSlug}/pipelines`,
                    (data) => ({
                      kind: "pipelines",
                      rows: data.pipelines,
                    }),
                  )
                }
              />
            </div>
          </div>
        </div>

        <ExplorerTableView table={table} />
      </section>

      <ResultPanel result={result} title="Explorer Response" />
    </div>
  );
}

function ExplorerTableView({ table }: { table: ExplorerTable }) {
  if (!table) {
    return (
      <div className="rounded-lg border border-[var(--border)] bg-white px-5 py-8 text-sm text-[var(--muted)]">
        Select an evidence source to render a table.
      </div>
    );
  }

  if (!table.rows.length) {
    return (
      <div className="rounded-lg border border-[var(--border)] bg-white px-5 py-8 text-sm text-[var(--muted)]">
        The backend returned no rows for this source.
      </div>
    );
  }

  if (table.kind === "work-items") {
    return (
      <DataTable
        columns={["Key", "Type", "Status", "Summary", "Source"]}
        rows={table.rows.map((row) => [row.issue_key, row.issue_type, row.status, row.summary, row.source])}
      />
    );
  }

  if (table.kind === "repositories") {
    return (
      <DataTable
        columns={["Slug", "Name", "Full Name", "Main Branch"]}
        rows={table.rows.map((row) => [row.slug, row.name, row.full_name, row.main_branch ?? ""])}
      />
    );
  }

  if (table.kind === "pull-requests") {
    return (
      <DataTable
        columns={["ID", "Title", "State", "Author", "Branches"]}
        rows={table.rows.map((row) => [
          String(row.id),
          row.title,
          row.state,
          row.author ?? "",
          `${row.source_branch ?? ""} -> ${row.target_branch ?? ""}`,
        ])}
      />
    );
  }

  if (table.kind === "commits") {
    return (
      <DataTable
        columns={["Hash", "Message", "Author", "Branch", "Committed"]}
        rows={table.rows.map((row) => [
          row.hash.slice(0, 12),
          row.message ?? "",
          row.author ?? "",
          row.branch ?? "",
          row.committed_at ?? "",
        ])}
      />
    );
  }

  if (table.kind === "pipelines") {
    return (
      <DataTable
        columns={["UUID", "State", "Result", "Branch", "Commit"]}
        rows={table.rows.map((row) => [
          row.uuid,
          row.state,
          row.result ?? "",
          row.branch ?? "",
          row.commit_sha?.slice(0, 12) ?? "",
        ])}
      />
    );
  }

  return (
    <DataTable
      columns={["Name", "Purpose", "MVP", "External Service"]}
      rows={table.rows.map((row) => [
        row.name,
        row.purpose,
        row.enabled_for_mvp ? "yes" : "no",
        row.requires_external_service ? "yes" : "no",
      ])}
    />
  );
}

function DataTable({ columns, rows }: { columns: string[]; rows: string[][] }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-[var(--border)] bg-white">
      <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase text-slate-500">
          <tr>
            {columns.map((column) => (
              <th className="px-4 py-3 font-semibold" key={column}>
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr className="border-t border-[var(--border)]" key={`${row[0]}-${rowIndex}`}>
              {row.map((cell, cellIndex) => (
                <td className="max-w-md px-4 py-3 align-top text-slate-700" key={`${cellIndex}-${cell}`}>
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
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

"use client";

import { useState } from "react";
import { getBackend, postBackend } from "@/lib/client-api";
import { ResultPanel } from "./result-panel";
import { StatusPill } from "./status-pill";

const jiraPayload = JSON.stringify(
  {
    jql: "updated >= -14d ORDER BY updated DESC",
    max_results: 25,
    project_id: null,
  },
  null,
  2,
);

const bitbucketRepoPayload = JSON.stringify(
  {
    project_id: null,
  },
  null,
  2,
);

const pullRequestPayload = JSON.stringify(
  {
    repository_id: "replace-with-ingested-repository-id",
    state: "OPEN",
  },
  null,
  2,
);

const commitsPayload = JSON.stringify(
  {
    repository_id: "replace-with-ingested-repository-id",
    branch: "develop",
  },
  null,
  2,
);

const pipelinesPayload = JSON.stringify(
  {
    repository_id: "replace-with-ingested-repository-id",
  },
  null,
  2,
);

const jobPayload = JSON.stringify(
  {
    job_name: "jira_ingest",
    payload: {
      jql: "updated >= -14d ORDER BY updated DESC",
      max_results: 25,
      project_id: null,
    },
  },
  null,
  2,
);

export function IngestionConsole() {
  const [jira, setJira] = useState(jiraPayload);
  const [bitbucketRepo, setBitbucketRepo] = useState(bitbucketRepoPayload);
  const [repoSlug, setRepoSlug] = useState("or-pems-plt-sandbox-api");
  const [pullRequests, setPullRequests] = useState(pullRequestPayload);
  const [commits, setCommits] = useState(commitsPayload);
  const [pipelines, setPipelines] = useState(pipelinesPayload);
  const [job, setJob] = useState(jobPayload);
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
        <div className="rounded-lg border border-[var(--border)] bg-white">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)] px-5 py-4">
            <div>
              <h2 className="text-base font-semibold">Jira</h2>
              <p className="text-sm text-[var(--muted)]">Read-only search and database ingestion.</p>
            </div>
            <StatusPill label="read:jira-work" tone="accent" />
          </div>
          <PayloadEditor onChange={setJira} value={jira} />
          <div className="grid gap-3 border-t border-[var(--border)] p-5 sm:grid-cols-2">
            <ActionButton
              disabled={isBusy}
              label="Search Issues"
              onClick={() => execute(() => postBackend("/integrations/jira/issues/search", stripProjectId(jira)))}
            />
            <ActionButton
              disabled={isBusy}
              label="Ingest Issues"
              onClick={() => execute(() => postBackend("/integrations/jira/issues/ingest", JSON.parse(jira) as unknown))}
            />
          </div>
        </div>

        <div className="rounded-lg border border-[var(--border)] bg-white">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)] px-5 py-4">
            <div>
              <h2 className="text-base font-semibold">Bitbucket</h2>
              <p className="text-sm text-[var(--muted)]">Repository metadata, pull requests, commits, and pipelines.</p>
            </div>
            <StatusPill label="read-only" tone="accent" />
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
            <div className="grid gap-3 sm:grid-cols-2">
              <ActionButton
                disabled={isBusy}
                label="List Repositories"
                onClick={() => execute(() => getBackend("/integrations/bitbucket/repositories"))}
              />
              <ActionButton
                disabled={isBusy}
                label="Ingest Repositories"
                onClick={() =>
                  execute(() =>
                    postBackend("/integrations/bitbucket/repositories/ingest", JSON.parse(bitbucketRepo) as unknown),
                  )
                }
              />
              <ActionButton
                disabled={isBusy}
                label="List Pull Requests"
                onClick={() =>
                  execute(() => getBackend(`/integrations/bitbucket/repositories/${encodeURIComponent(repoSlug)}/pull-requests`))
                }
              />
              <ActionButton
                disabled={isBusy}
                label="List Commits"
                onClick={() =>
                  execute(() => getBackend(`/integrations/bitbucket/repositories/${encodeURIComponent(repoSlug)}/commits`))
                }
              />
              <ActionButton
                disabled={isBusy}
                label="List Pipelines"
                onClick={() =>
                  execute(() => getBackend(`/integrations/bitbucket/repositories/${encodeURIComponent(repoSlug)}/pipelines`))
                }
              />
            </div>
          </div>
          <details className="border-t border-[var(--border)]">
            <summary className="cursor-pointer px-5 py-4 text-sm font-semibold">Ingest linked Bitbucket artifacts</summary>
            <div className="grid gap-4 p-5">
              <SmallPayload title="Pull request ingest" value={pullRequests} onChange={setPullRequests} />
              <SmallPayload title="Commit ingest" value={commits} onChange={setCommits} />
              <SmallPayload title="Pipeline ingest" value={pipelines} onChange={setPipelines} />
              <div className="grid gap-3 sm:grid-cols-3">
                <ActionButton
                  disabled={isBusy}
                  label="Ingest PRs"
                  onClick={() =>
                    execute(() =>
                      postBackend(
                        `/integrations/bitbucket/repositories/${encodeURIComponent(repoSlug)}/pull-requests/ingest`,
                        JSON.parse(pullRequests) as unknown,
                      ),
                    )
                  }
                />
                <ActionButton
                  disabled={isBusy}
                  label="Ingest Commits"
                  onClick={() =>
                    execute(() =>
                      postBackend(
                        `/integrations/bitbucket/repositories/${encodeURIComponent(repoSlug)}/commits/ingest`,
                        JSON.parse(commits) as unknown,
                      ),
                    )
                  }
                />
                <ActionButton
                  disabled={isBusy}
                  label="Ingest Pipelines"
                  onClick={() =>
                    execute(() =>
                      postBackend(
                        `/integrations/bitbucket/repositories/${encodeURIComponent(repoSlug)}/pipelines/ingest`,
                        JSON.parse(pipelines) as unknown,
                      ),
                    )
                  }
                />
              </div>
            </div>
          </details>
        </div>

        <div className="rounded-lg border border-[var(--border)] bg-white">
          <div className="border-b border-[var(--border)] px-5 py-4">
            <h2 className="text-base font-semibold">Job Runner</h2>
            <p className="text-sm text-[var(--muted)]">Synchronous development facade for future Temporal workflows.</p>
          </div>
          <PayloadEditor onChange={setJob} value={job} />
          <div className="border-t border-[var(--border)] p-5">
            <ActionButton
              disabled={isBusy}
              label="Run Job"
              onClick={() => execute(() => postBackend("/jobs/run", JSON.parse(job) as unknown))}
            />
          </div>
        </div>
      </section>

      <ResultPanel result={result} title="Ingestion Response" />
    </div>
  );
}

function stripProjectId(value: string) {
  const parsed = JSON.parse(value) as { project_id?: unknown };
  delete parsed.project_id;
  return parsed;
}

function PayloadEditor({ onChange, value }: { onChange: (value: string) => void; value: string }) {
  return (
    <div className="p-5">
      <textarea
        className="focus-ring min-h-56 w-full resize-y rounded-md border border-[var(--border)] bg-slate-50 p-3 font-mono text-xs leading-6 text-slate-800"
        onChange={(event) => onChange(event.target.value)}
        spellCheck={false}
        value={value}
      />
    </div>
  );
}

function SmallPayload({
  onChange,
  title,
  value,
}: {
  onChange: (value: string) => void;
  title: string;
  value: string;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-semibold">{title}</span>
      <textarea
        className="focus-ring min-h-36 w-full resize-y rounded-md border border-[var(--border)] bg-slate-50 p-3 font-mono text-xs leading-6 text-slate-800"
        onChange={(event) => onChange(event.target.value)}
        spellCheck={false}
        value={value}
      />
    </label>
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

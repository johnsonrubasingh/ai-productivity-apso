"use client";

import { useState } from "react";
import { getBackend, postBackend } from "@/lib/client-api";
import { ResultPanel } from "./result-panel";

type AdminResult = unknown;

export function AdminConsole() {
  const [tenantName, setTenantName] = useState("");
  const [tenantSlug, setTenantSlug] = useState("");
  const [projectName, setProjectName] = useState("");
  const [projectKey, setProjectKey] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [userDisplayName, setUserDisplayName] = useState("");
  const [userRole, setUserRole] = useState("developer");
  const [result, setResult] = useState<AdminResult>(null);
  const [isBusy, setIsBusy] = useState(false);

  async function run(action: () => Promise<AdminResult>) {
    setIsBusy(true);
    setResult(await action());
    setIsBusy(false);
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_420px]">
      <section className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold">Administration</h2>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-[var(--muted)]">
            Configure the tenant, project, and user records that control protected APSO workflows.
          </p>
        </div>

        <div className="grid gap-5 lg:grid-cols-3">
          <section className="rounded-lg border border-[var(--border)] bg-white">
            <div className="border-b border-[var(--border)] px-5 py-4">
              <h3 className="text-base font-semibold">Tenant</h3>
            </div>
            <div className="space-y-3 p-5">
              <input
                className="focus-ring h-10 w-full rounded-md border border-[var(--border)] px-3 text-sm"
                onChange={(event) => setTenantName(event.target.value)}
                placeholder="Tenant name"
                value={tenantName}
              />
              <input
                className="focus-ring h-10 w-full rounded-md border border-[var(--border)] px-3 text-sm"
                onChange={(event) => setTenantSlug(event.target.value)}
                placeholder="tenant-slug"
                value={tenantSlug}
              />
              <button
                className="focus-ring h-10 w-full rounded-md bg-[var(--accent)] px-4 text-sm font-semibold text-white hover:bg-teal-800 disabled:bg-slate-400"
                disabled={isBusy || !tenantName.trim() || !tenantSlug.trim()}
                onClick={() =>
                  run(() => postBackend("/core/tenants", { name: tenantName, slug: tenantSlug }))
                }
                type="button"
              >
                Create Tenant
              </button>
              <button
                className="focus-ring h-10 w-full rounded-md border border-[var(--border)] px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                disabled={isBusy}
                onClick={() => run(() => getBackend("/core/tenants"))}
                type="button"
              >
                List Tenants
              </button>
            </div>
          </section>

          <section className="rounded-lg border border-[var(--border)] bg-white">
            <div className="border-b border-[var(--border)] px-5 py-4">
              <h3 className="text-base font-semibold">Project</h3>
            </div>
            <div className="space-y-3 p-5">
              <input
                className="focus-ring h-10 w-full rounded-md border border-[var(--border)] px-3 text-sm"
                onChange={(event) => setProjectName(event.target.value)}
                placeholder="Project name"
                value={projectName}
              />
              <input
                className="focus-ring h-10 w-full rounded-md border border-[var(--border)] px-3 text-sm"
                onChange={(event) => setProjectKey(event.target.value)}
                placeholder="APSO"
                value={projectKey}
              />
              <textarea
                className="focus-ring min-h-24 w-full rounded-md border border-[var(--border)] px-3 py-2 text-sm"
                onChange={(event) => setProjectDescription(event.target.value)}
                placeholder="Description"
                value={projectDescription}
              />
              <button
                className="focus-ring h-10 w-full rounded-md bg-[var(--accent)] px-4 text-sm font-semibold text-white hover:bg-teal-800 disabled:bg-slate-400"
                disabled={isBusy || !projectName.trim() || !projectKey.trim()}
                onClick={() =>
                  run(() =>
                    postBackend("/core/projects", {
                      name: projectName,
                      key: projectKey,
                      description: projectDescription || null,
                    }),
                  )
                }
                type="button"
              >
                Create Project
              </button>
              <button
                className="focus-ring h-10 w-full rounded-md border border-[var(--border)] px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                disabled={isBusy}
                onClick={() => run(() => getBackend("/core/projects"))}
                type="button"
              >
                List Projects
              </button>
            </div>
          </section>

          <section className="rounded-lg border border-[var(--border)] bg-white">
            <div className="border-b border-[var(--border)] px-5 py-4">
              <h3 className="text-base font-semibold">Users</h3>
            </div>
            <div className="space-y-3 p-5">
              <input
                className="focus-ring h-10 w-full rounded-md border border-[var(--border)] px-3 text-sm"
                onChange={(event) => setUserEmail(event.target.value)}
                placeholder="user@example.com"
                type="email"
                value={userEmail}
              />
              <input
                className="focus-ring h-10 w-full rounded-md border border-[var(--border)] px-3 text-sm"
                onChange={(event) => setUserDisplayName(event.target.value)}
                placeholder="Display name"
                value={userDisplayName}
              />
              <select
                className="focus-ring h-10 w-full rounded-md border border-[var(--border)] bg-white px-3 text-sm"
                onChange={(event) => setUserRole(event.target.value)}
                value={userRole}
              >
                <option value="developer">Developer</option>
                <option value="lead">Lead</option>
                <option value="admin">Admin</option>
              </select>
              <button
                className="focus-ring h-10 w-full rounded-md bg-[var(--accent)] px-4 text-sm font-semibold text-white hover:bg-teal-800 disabled:bg-slate-400"
                disabled={isBusy || !userEmail.trim()}
                onClick={() =>
                  run(() =>
                    postBackend("/core/users", {
                      email: userEmail,
                      display_name: userDisplayName || null,
                      role: userRole,
                    }),
                  )
                }
                type="button"
              >
                Create User
              </button>
              <button
                className="focus-ring h-10 w-full rounded-md border border-[var(--border)] px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                disabled={isBusy}
                onClick={() => run(() => getBackend("/core/users"))}
                type="button"
              >
                List Users
              </button>
            </div>
          </section>
        </div>
      </section>

      <ResultPanel result={result} title="Admin API Response" />
    </div>
  );
}

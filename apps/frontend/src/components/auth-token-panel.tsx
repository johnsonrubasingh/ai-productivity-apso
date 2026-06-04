"use client";

import { useState } from "react";
import { clearAuthToken, getBackend, readAuthToken, saveAuthToken } from "@/lib/client-api";
import { ResultPanel } from "./result-panel";
import { StatusPill } from "./status-pill";

export function AuthTokenPanel() {
  const [token, setToken] = useState("");
  const [hasToken, setHasToken] = useState(() => Boolean(readAuthToken()));
  const [result, setResult] = useState<unknown>(null);
  const [isBusy, setIsBusy] = useState(false);

  function save() {
    saveAuthToken(token);
    setToken("");
    setHasToken(Boolean(readAuthToken()));
    setResult({ ok: true, message: "Token stored in this browser session only." });
  }

  function clear() {
    clearAuthToken();
    setHasToken(false);
    setResult({ ok: true, message: "Token cleared from this browser session." });
  }

  async function verify() {
    setIsBusy(true);
    setResult(await getBackend("/auth/me"));
    setHasToken(Boolean(readAuthToken()));
    setIsBusy(false);
  }

  return (
    <div className="mx-auto grid max-w-5xl gap-6 lg:grid-cols-[0.9fr_1.1fr]">
      <section className="rounded-lg border border-[var(--border)] bg-white">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)] px-5 py-4">
          <div>
            <h2 className="text-base font-semibold">Session Token</h2>
            <p className="text-sm text-[var(--muted)]">Protected production calls use a Supabase bearer token.</p>
          </div>
          <StatusPill label={hasToken ? "token present" : "no token"} tone={hasToken ? "success" : "warning"} />
        </div>
        <div className="space-y-4 p-5">
          <label className="block">
            <span className="mb-2 block text-sm font-semibold">Bearer token</span>
            <textarea
              className="focus-ring min-h-44 w-full resize-y rounded-md border border-[var(--border)] bg-slate-50 p-3 font-mono text-xs leading-6 text-slate-800"
              onChange={(event) => setToken(event.target.value)}
              placeholder="Paste Supabase access token"
              spellCheck={false}
              value={token}
            />
          </label>
          <div className="grid gap-3 sm:grid-cols-3">
            <button
              className="focus-ring h-10 rounded-md bg-[var(--accent)] px-4 text-sm font-semibold text-white hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-400"
              disabled={!token.trim()}
              onClick={save}
              type="button"
            >
              Save
            </button>
            <button
              className="focus-ring h-10 rounded-md border border-[var(--border)] bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              onClick={verify}
              type="button"
              disabled={isBusy}
            >
              {isBusy ? "Checking..." : "Verify"}
            </button>
            <button
              className="focus-ring h-10 rounded-md border border-[var(--border)] bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              onClick={clear}
              type="button"
            >
              Clear
            </button>
          </div>
          <p className="text-xs leading-5 text-[var(--muted)]">
            The token is stored in `sessionStorage`, never in source code, and is cleared when the browser session ends.
          </p>
        </div>
      </section>

      <ResultPanel result={result} title="Auth Check Response" />
    </div>
  );
}

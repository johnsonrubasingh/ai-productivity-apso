"use client";

import { useEffect, useState } from "react";
import { clearAuthToken, getBackend, readAuthToken, saveAuthToken } from "@/lib/client-api";
import { getSupabaseClient, isSupabaseConfigured } from "@/lib/supabase";
import { ResultPanel } from "./result-panel";
import { StatusPill } from "./status-pill";

export function AuthTokenPanel() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [hasToken, setHasToken] = useState(() => Boolean(readAuthToken()));
  const [sessionEmail, setSessionEmail] = useState<string | null>(null);
  const [result, setResult] = useState<unknown>(null);
  const [isBusy, setIsBusy] = useState(false);
  const supabaseConfigured = isSupabaseConfigured();

  useEffect(() => {
    const supabase = getSupabaseClient();
    if (!supabase) {
      return;
    }

    supabase.auth.getSession().then(({ data }) => {
      const accessToken = data.session?.access_token;
      if (accessToken) {
        saveAuthToken(accessToken);
        setHasToken(true);
        setSessionEmail(data.session?.user.email ?? null);
      }
    });

    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.access_token) {
        saveAuthToken(session.access_token);
        setHasToken(true);
        setSessionEmail(session.user.email ?? null);
      } else {
        clearAuthToken();
        setHasToken(false);
        setSessionEmail(null);
      }
    });

    return () => listener.subscription.unsubscribe();
  }, []);

  async function signIn() {
    const supabase = getSupabaseClient();
    if (!supabase) {
      setResult({ ok: false, message: "Supabase public URL and anon key are not configured." });
      return;
    }
    setIsBusy(true);
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      setResult({ ok: false, message: error.message });
    } else if (data.session?.access_token) {
      saveAuthToken(data.session.access_token);
      setHasToken(true);
      setSessionEmail(data.user?.email ?? null);
      setResult({ ok: true, message: "Signed in with Supabase Auth.", user: data.user?.email });
    }
    setIsBusy(false);
  }

  async function signUp() {
    const supabase = getSupabaseClient();
    if (!supabase) {
      setResult({ ok: false, message: "Supabase public URL and anon key are not configured." });
      return;
    }
    setIsBusy(true);
    const { data, error } = await supabase.auth.signUp({ email, password });
    if (error) {
      setResult({ ok: false, message: error.message });
    } else {
      if (data.session?.access_token) {
        saveAuthToken(data.session.access_token);
        setHasToken(true);
      }
      setSessionEmail(data.user?.email ?? null);
      setResult({ ok: true, message: "Supabase sign-up submitted.", user: data.user?.email });
    }
    setIsBusy(false);
  }

  function save() {
    saveAuthToken(token);
    setToken("");
    setHasToken(Boolean(readAuthToken()));
    setResult({ ok: true, message: "Token stored in this browser session only." });
  }

  function clear() {
    clearAuthToken();
    setHasToken(false);
    setSessionEmail(null);
    setResult({ ok: true, message: "Token cleared from this browser session." });
  }

  async function signOut() {
    setIsBusy(true);
    await getSupabaseClient()?.auth.signOut();
    clear();
    setIsBusy(false);
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
            <h2 className="text-base font-semibold">Supabase Session</h2>
            <p className="text-sm text-[var(--muted)]">
              Protected production calls use the Supabase access token from the active session.
            </p>
          </div>
          <StatusPill
            label={sessionEmail ?? (hasToken ? "token present" : "not signed in")}
            tone={hasToken ? "success" : "warning"}
          />
        </div>
        <div className="space-y-4 p-5">
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="block">
              <span className="mb-2 block text-sm font-semibold">Email</span>
              <input
                className="focus-ring h-10 w-full rounded-md border border-[var(--border)] bg-white px-3 text-sm"
                onChange={(event) => setEmail(event.target.value)}
                type="email"
                value={email}
              />
            </label>
            <label className="block">
              <span className="mb-2 block text-sm font-semibold">Password</span>
              <input
                className="focus-ring h-10 w-full rounded-md border border-[var(--border)] bg-white px-3 text-sm"
                onChange={(event) => setPassword(event.target.value)}
                type="password"
                value={password}
              />
            </label>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <button
              className="focus-ring h-10 rounded-md bg-[var(--accent)] px-4 text-sm font-semibold text-white hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-400"
              disabled={!supabaseConfigured || !email.trim() || !password || isBusy}
              onClick={signIn}
              type="button"
            >
              Sign In
            </button>
            <button
              className="focus-ring h-10 rounded-md border border-[var(--border)] bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:bg-slate-100"
              disabled={!supabaseConfigured || !email.trim() || !password || isBusy}
              onClick={signUp}
              type="button"
            >
              Sign Up
            </button>
            <button
              className="focus-ring h-10 rounded-md border border-[var(--border)] bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:bg-slate-100"
              disabled={isBusy || !hasToken}
              onClick={signOut}
              type="button"
            >
              Sign Out
            </button>
          </div>
          {!supabaseConfigured ? (
            <p className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs leading-5 text-amber-900">
              Supabase public configuration is missing. Set NEXT_PUBLIC_SUPABASE_URL and
              NEXT_PUBLIC_SUPABASE_ANON_KEY for dev or prod.
            </p>
          ) : null}
          <label className="block">
            <span className="mb-2 block text-sm font-semibold">Manual bearer token fallback</span>
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

import { fallbackDashboardData } from "./fallback-data";
import type { DashboardData, Finding, IntegrationStatus } from "./types";

const API_BASE_URL =
  process.env.APSO_BACKEND_API_URL?.replace(/\/$/, "") ??
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  "http://localhost:8000/api/v1";
const IS_PRODUCTION = process.env.NODE_ENV === "production";

type BackendIntegration = {
  id?: string;
  key?: string;
  name?: string;
  configured?: boolean;
  status?: string;
  mode?: string;
  required_scopes?: string[];
  notes?: string;
};

type BackendFinding = {
  id?: string;
  title?: string;
  severity?: string;
  source?: string;
  status?: string;
  owner?: string;
  evidence?: string;
};

async function getJson<T>(path: string): Promise<T | null> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 2500);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: IS_PRODUCTION
        ? {}
        : {
            "X-APSO-Dev-User": "frontend-dev",
            "X-APSO-Dev-Tenant": "default",
            "X-APSO-Dev-Role": "developer",
          },
      next: { revalidate: 20 },
      signal: controller.signal,
    });

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as T;
  } catch {
    return null;
  } finally {
    clearTimeout(timeout);
  }
}

function normalizeIntegrations(items: BackendIntegration[] | null): IntegrationStatus[] {
  if (!items?.length) {
    return fallbackDashboardData.integrations;
  }

  return items.map((item) => {
    const id = item.id ?? item.key ?? item.name?.toLowerCase() ?? "integration";
    const configured = Boolean(item.configured) || item.status === "configured";

    return {
      id,
      name: item.name ?? id.toUpperCase(),
      mode: id.includes("aws") ? "mock" : "read-only",
      state: configured ? "configured" : "unconfigured",
      scope: item.required_scopes?.join(", ") ?? "Configured in backend",
      lastChecked: "Backend metadata",
      notes: item.notes ?? "Managed by APSO backend configuration.",
    };
  });
}

function normalizeFindings(items: BackendFinding[] | null): Finding[] {
  if (!items?.length) {
    return fallbackDashboardData.findings;
  }

  return items.map((item, index) => ({
    id: item.id ?? `APSO-F-${String(index + 1).padStart(3, "0")}`,
    title: item.title ?? "Untitled finding",
    severity: normalizeSeverity(item.severity),
    source: item.source ?? "APSO",
    status: normalizeStatus(item.status),
    owner: item.owner ?? "Unassigned",
    evidence: item.evidence ?? "Evidence is available in the backend record.",
  }));
}

function normalizeSeverity(value: string | undefined): Finding["severity"] {
  if (value === "critical" || value === "high" || value === "medium" || value === "low") {
    return value;
  }

  return "medium";
}

function normalizeStatus(value: string | undefined): Finding["status"] {
  if (value === "open" || value === "triaged" || value === "resolved") {
    return value;
  }

  return "open";
}

export async function getDashboardData(): Promise<DashboardData> {
  const [health, integrations, findings] = await Promise.all([
    getJson<Record<string, string>>("/health"),
    getJson<BackendIntegration[]>("/integrations"),
    getJson<BackendFinding[]>("/findings"),
  ]);

  return {
    ...fallbackDashboardData,
    generatedAt: health ? new Date().toISOString() : fallbackDashboardData.generatedAt,
    integrations: normalizeIntegrations(integrations),
    findings: normalizeFindings(findings),
  };
}

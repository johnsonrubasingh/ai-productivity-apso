export type ConnectionState = "connected" | "configured" | "unconfigured" | "degraded";

export type IntegrationStatus = {
  id: string;
  name: string;
  mode: "read-only" | "mock" | "local-ai" | "database";
  state: ConnectionState;
  scope: string;
  lastChecked: string;
  notes: string;
};

export type EngineStatus = {
  id: string;
  name: string;
  state: "ready" | "needs-input" | "running";
  route: string;
  signal: string;
  coverage: string;
};

export type Finding = {
  id: string;
  title: string;
  severity: "critical" | "high" | "medium" | "low";
  source: string;
  status: "open" | "triaged" | "resolved";
  owner: string;
  evidence: string;
};

export type ReadinessSignal = {
  name: string;
  score: number;
  status: "pass" | "watch" | "block";
};

export type DashboardData = {
  generatedAt: string;
  integrations: IntegrationStatus[];
  engines: EngineStatus[];
  findings: Finding[];
  readiness: ReadinessSignal[];
  proofPackItems: string[];
};

# APSO Observability

APSO uses self-hosted open-source observability components in development and
production-style deployments.

## Components

- Prometheus scrapes backend metrics from `/api/v1/ops/metrics`.
- Grafana OSS reads Prometheus, Loki, and Jaeger data sources.
- Loki stores application logs.
- Jaeger receives distributed traces when OpenTelemetry instrumentation is
  enabled in later service slices.

## Backend Signals

The backend currently emits:

- JSON request logs to stdout.
- `x-request-id` response header.
- `x-apso-duration-ms` response header.
- Prometheus-format HTTP counters at `/api/v1/ops/metrics`.

Metric names:

```text
apso_http_requests_total
apso_http_request_duration_ms_sum
```

## Run Locally

Start APSO backend/frontend first:

```powershell
docker compose -f docker-compose.dev.yml up --build
```

Start observability:

```powershell
docker compose -f docker-compose.dev.yml -f docker-compose.observability.yml up -d
```

Open:

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`
- Loki: `http://localhost:3100`
- Jaeger: `http://localhost:16686`

Default Grafana credentials are `admin/admin` unless overridden through
`GRAFANA_ADMIN_USER` and `GRAFANA_ADMIN_PASSWORD`.

## Production Rules

- Logs must go to stdout/stderr in JSON format.
- Secrets must never be written to logs.
- Prometheus metrics must not expose tokens, usernames, issue summaries, code
  snippets, or customer-sensitive values.
- Grafana admin password must be supplied by the deployment secret store.
- Jaeger should not be internet exposed.

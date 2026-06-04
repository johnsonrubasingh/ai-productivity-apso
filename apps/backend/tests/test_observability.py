from fastapi.testclient import TestClient


def test_metrics_endpoint_records_requests(client: TestClient) -> None:
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert "x-apso-duration-ms" in health.headers

    metrics = client.get("/api/v1/ops/metrics")
    assert metrics.status_code == 200
    assert "text/plain" in metrics.headers["content-type"]
    body = metrics.text
    assert "apso_http_requests_total" in body
    assert 'path="/api/v1/health"' in body

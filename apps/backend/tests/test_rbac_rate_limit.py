from fastapi.testclient import TestClient

from apso_backend.core.rate_limit import RateLimiter


def test_apso_dev_headers_are_accepted(client: TestClient) -> None:
    response = client.get(
        "/api/v1/auth/me",
        headers={
            "x-apso-dev-tenant": "tenant-a",
            "x-apso-dev-user": "user-a",
            "x-apso-dev-role": "lead",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "tenant_id": "tenant-a",
        "user_id": "user-a",
        "role": "lead",
    }


def test_lead_only_job_rejects_developer(client: TestClient) -> None:
    response = client.post(
        "/api/v1/jobs/run",
        headers={"x-tenant-id": "tenant-a", "x-user-id": "user-a", "x-role": "developer"},
        json={
            "job_name": "release_readiness_assessment",
            "payload": {"release_name": "RBAC Test"},
        },
    )

    assert response.status_code == 403


def test_rate_limiter_blocks_after_window_capacity() -> None:
    limiter = RateLimiter(max_requests=2, window_seconds=60)

    assert limiter.allow("user-a")[0] is True
    assert limiter.allow("user-a")[0] is True
    assert limiter.allow("user-a")[0] is False

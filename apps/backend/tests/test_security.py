from fastapi.testclient import TestClient


PROD_ENV = {
    "APSO_FRONTEND_URL": "https://apso.example.com",
    "APSO_API_URL": "https://api.apso.example.com",
    "JIRA_BASE_URL": "https://example.atlassian.net",
    "BITBUCKET_WORKSPACE": "example-workspace",
    "SUPABASE_URL": "https://example.supabase.co",
    "AI_GATEWAY_URL": "http://ai-gateway:8010",
    "OLLAMA_BASE_URL": "http://ollama:11434",
    "MINIO_ENDPOINT": "http://minio:9000",
    "TEMPORAL_ENDPOINT": "temporal:7233",
    "VALKEY_ENDPOINT": "valkey:6379",
    "APSO_REPOSITORY_ROOT": "/var/lib/apso/repositories",
    "APSO_ARTIFACT_ROOT": "/var/lib/apso/artifacts",
}


def test_prod_rejects_dev_headers_when_jwt_secret_exists(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("APSO_ENV", "prod")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-secret")
    for key, value in PROD_ENV.items():
        monkeypatch.setenv(key, value)

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "x-tenant-id": "dev-tenant",
            "x-user-id": "dev-user",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing bearer token"


def test_dev_allows_dev_headers_without_jwt_secret(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("APSO_ENV", "dev")
    monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "x-tenant-id": "dev-tenant",
            "x-user-id": "dev-user",
            "x-role": "developer",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["tenant_id"] == "dev-tenant"
    assert payload["user_id"] == "dev-user"

import pytest

from apso_backend.core.config import load_settings


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


def test_prod_config_requires_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in PROD_ENV:
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(ValueError, match="APSO_FRONTEND_URL"):
        load_settings("prod")


def test_prod_config_expands_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in PROD_ENV.items():
        monkeypatch.setenv(key, value)

    settings = load_settings("prod")

    assert settings.environment == "prod"
    assert settings.app.frontend_url == PROD_ENV["APSO_FRONTEND_URL"]
    assert settings.integrations.bitbucket.workspace == PROD_ENV["BITBUCKET_WORKSPACE"]
    assert settings.workspace.artifact_root == PROD_ENV["APSO_ARTIFACT_ROOT"]

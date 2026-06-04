from fastapi.testclient import TestClient


def test_public_runtime_routes(client: TestClient) -> None:
    assert client.get("/api/v1/health").status_code == 200
    assert client.get("/api/v1/config/runtime").status_code == 200
    assert client.get("/api/v1/integrations").status_code == 200
    assert client.get("/api/v1/ai/tasks").status_code == 200


def test_jira_and_bitbucket_scopes_are_read_only(client: TestClient) -> None:
    jira = client.get("/api/v1/integrations/jira/scopes").json()
    bitbucket = client.get("/api/v1/integrations/bitbucket/scopes").json()

    assert jira["required_now"] == ["read:account", "read:jira-work"]
    assert "write:jira-work" in jira["backlog_only"]
    assert "read_only" in jira["mvp_policy"]

    assert all(scope.startswith("read:") for scope in bitbucket["required_now"])
    assert "read:test:bitbucket" in bitbucket["required_now"]
    assert "read_only" in bitbucket["mvp_policy"]
    assert any("write" in scope for scope in bitbucket["do_not_select_for_mvp"])


def test_definition_gap_engine_contract(client: TestClient) -> None:
    response = client.post(
        "/api/v1/engines/definition-gap/analyze",
        headers={"x-tenant-id": "dev-tenant"},
        json={
            "tenant_id": "dev-tenant",
            "project_id": "dev-project",
            "issue_key": "APSO-1",
            "summary": "Create release readiness dashboard",
            "description": "Dashboard should show blockers and evidence.",
            "acceptance_criteria": "",
            "comments": [],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["issue_key"] == "APSO-1"
    assert 0 <= payload["quality_score"] <= 100
    assert payload["findings"]
    assert payload["findings"][0]["metric_label"] in {"actual", "estimated", "ai_inferred", "sample", "placeholder"}


def test_quality_release_and_report_contracts(client: TestClient) -> None:
    code_quality = client.post(
        "/api/v1/engines/code-quality/analyze",
        headers={"x-tenant-id": "dev-tenant"},
        json={"repository_slug": "apso", "execute_scanners": False},
    )
    assert code_quality.status_code == 200
    assert code_quality.json()["read_only"] is True

    coverage = client.post(
        "/api/v1/engines/coverage/verify",
        headers={"x-tenant-id": "dev-tenant"},
        json={
            "work_item_key": "APSO-1",
            "linked_commits": 1,
            "linked_pull_requests": 1,
            "linked_test_runs": 1,
            "successful_pipeline_runs": 1,
            "coverage_percent": 85,
        },
    )
    assert coverage.status_code == 200
    assert coverage.json()["read_only"] is True

    release = client.post(
        "/api/v1/quality/release-readiness",
        headers={"x-tenant-id": "dev-tenant"},
        json={
            "release_name": "MVP",
            "open_high_risk_findings": 0,
            "failed_pipeline_runs": 0,
            "stories_without_tests": 0,
            "unresolved_requirement_gaps": 0,
        },
    )
    assert release.status_code == 200
    assert release.json()["read_only"] is True

    proof_pack = client.post(
        "/api/v1/reports/proof-pack",
        headers={"x-tenant-id": "dev-tenant"},
        json={"title": "APSO Proof Pack", "include_placeholders": True},
    )
    assert proof_pack.status_code == 200
    assert proof_pack.json()["read_only"] is True


def test_protected_routes_require_context(client: TestClient) -> None:
    response = client.get("/api/v1/integrations/bitbucket/repositories")
    assert response.status_code == 401

    source = client.get("/api/v1/integrations/bitbucket/repositories/apso/source")
    assert source.status_code == 401

    steps = client.get("/api/v1/integrations/bitbucket/repositories/apso/pipelines/pipe-1/steps")
    assert steps.status_code == 401


def test_bitbucket_evidence_contracts_are_in_openapi(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]

    assert "/api/v1/integrations/bitbucket/repositories/{repo_slug}/pipelines/{pipeline_uuid}/steps" in paths
    assert "/api/v1/integrations/bitbucket/repositories/{repo_slug}/pipelines/tests/ingest" in paths
    assert "/api/v1/integrations/bitbucket/repositories/{repo_slug}/source" in paths
    assert "/api/v1/integrations/bitbucket/repositories/{repo_slug}/source/ingest" in paths
    assert "/api/v1/integrations/bitbucket/repositories/{repo_slug}/diff/ingest" in paths

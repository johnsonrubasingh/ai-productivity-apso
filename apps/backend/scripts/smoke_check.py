from fastapi.testclient import TestClient

from apso_backend.main import app


def main() -> None:
    client = TestClient(app)

    health = client.get("/api/v1/health")
    health.raise_for_status()

    integrations = client.get("/api/v1/integrations")
    integrations.raise_for_status()

    ai_tasks = client.get("/api/v1/ai/tasks")
    ai_tasks.raise_for_status()

    jira_scopes = client.get("/api/v1/integrations/jira/scopes")
    jira_scopes.raise_for_status()

    bitbucket_scopes = client.get("/api/v1/integrations/bitbucket/scopes")
    bitbucket_scopes.raise_for_status()

    jira_check = client.get("/api/v1/integrations/jira/check")
    jira_check.raise_for_status()

    bitbucket_check = client.get("/api/v1/integrations/bitbucket/check")
    bitbucket_check.raise_for_status()

    runtime = client.get("/api/v1/config/runtime")
    runtime.raise_for_status()

    me = client.get(
        "/api/v1/auth/me",
        headers={"x-tenant-id": "dev-tenant", "x-user-id": "dev-user", "x-role": "developer"},
    )
    me.raise_for_status()

    sample_jql = client.get("/api/v1/integrations/jira/issues/sample-jql")
    sample_jql.raise_for_status()

    bitbucket_repos_without_auth = client.get("/api/v1/integrations/bitbucket/repositories")
    assert bitbucket_repos_without_auth.status_code == 401

    definition_gap = client.post(
        "/api/v1/engines/definition-gap/analyze",
        headers={"x-tenant-id": "dev-tenant"},
        json={
            "tenant_id": "dev-tenant",
            "project_id": "dev-project",
            "issue_key": "APSO-1",
            "summary": "Create user friendly dashboard",
            "description": "Build a simple dashboard etc",
            "acceptance_criteria": "",
            "comments": [],
        },
    )
    definition_gap.raise_for_status()

    scanners = client.get("/api/v1/quality/scanners")
    scanners.raise_for_status()

    release = client.post(
        "/api/v1/quality/release-readiness",
        headers={"x-tenant-id": "dev-tenant"},
        json={
            "release_name": "MVP Demo",
            "open_high_risk_findings": 1,
            "failed_pipeline_runs": 0,
            "stories_without_tests": 2,
            "unresolved_requirement_gaps": 1,
        },
    )
    release.raise_for_status()

    proof_pack = client.post(
        "/api/v1/reports/proof-pack",
        headers={"x-tenant-id": "dev-tenant"},
        json={"title": "Smoke Proof Pack"},
    )
    proof_pack.raise_for_status()

    job = client.post(
        "/api/v1/jobs/run",
        headers={"x-tenant-id": "dev-tenant", "x-role": "lead"},
        json={
            "job_name": "release_readiness_assessment",
            "payload": {
                "release_name": "Job Smoke",
                "open_high_risk_findings": 0,
                "failed_pipeline_runs": 0,
            },
        },
    )
    job.raise_for_status()

    readiness = client.get("/api/v1/ops/readiness")
    readiness.raise_for_status()

    code_quality = client.post(
        "/api/v1/engines/code-quality/analyze",
        headers={"x-tenant-id": "dev-tenant"},
        json={"repository_slug": "or-pems-plt-sandbox-api", "execute_scanners": False},
    )
    code_quality.raise_for_status()

    coverage = client.post(
        "/api/v1/engines/coverage/verify",
        headers={"x-tenant-id": "dev-tenant"},
        json={
            "work_item_key": "APSO-1",
            "linked_commits": 1,
            "linked_pull_requests": 1,
            "linked_test_runs": 0,
            "successful_pipeline_runs": 1,
        },
    )
    coverage.raise_for_status()

    dashboard = client.get("/api/v1/dashboard/project-health", headers={"x-tenant-id": "dev-tenant"})
    dashboard.raise_for_status()

    print("health:", health.json())
    print("integrations:", [item["provider"] for item in integrations.json()])
    print("ai_tasks:", [item["name"] for item in ai_tasks.json()])
    print("jira_required_scopes:", jira_scopes.json()["required_now"])
    print("bitbucket_required_scopes:", bitbucket_scopes.json()["required_now"])
    print("jira_check_ok:", jira_check.json().get("ok"))
    print("bitbucket_check_ok:", bitbucket_check.json().get("ok"))
    print("runtime_environment:", runtime.json()["environment"])
    print("auth_context:", me.json())
    print("sample_jql_keys:", list(sample_jql.json().keys()))
    print("protected_bitbucket_route_without_auth:", bitbucket_repos_without_auth.status_code)
    print("definition_gap_score:", definition_gap.json()["quality_score"])
    print("scanner_count:", len(scanners.json()))
    print("release_readiness_score:", release.json()["readiness_score"])
    print("proof_pack_sections:", [section["title"] for section in proof_pack.json()["sections"]])
    print("job_status:", job.json()["status"])
    print("readiness_status:", readiness.json()["status"])
    print("code_quality_score:", code_quality.json()["quality_score"])
    print("coverage_confidence_score:", coverage.json()["coverage_confidence_score"])
    print("dashboard_metric_count:", len(dashboard.json()["metrics"]))


if __name__ == "__main__":
    main()

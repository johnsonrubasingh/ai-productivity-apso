from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apso_backend.integrations.aws_mock.client import AwsMockConnector
from apso_backend.integrations.bitbucket.client import (
    BITBUCKET_OPTIONAL_READ_SCOPES,
    BITBUCKET_REQUIRED_READ_SCOPES,
    BITBUCKET_SCOPE_EXCLUSIONS,
    BitbucketClient,
)
from apso_backend.integrations.bitbucket.normalizer import (
    normalize_commit,
    normalize_pipeline,
    normalize_pull_request,
    normalize_repository,
)
from apso_backend.integrations.jira.client import JiraClient
from apso_backend.integrations.jira.normalizer import normalize_search_response
from apso_backend.schemas.integrations import IntegrationSummary
from apso_backend.schemas.bitbucket import (
    BitbucketCommitIngestRequest,
    BitbucketCommitIngestResponse,
    BitbucketCommitListResponse,
    BitbucketPipelineIngestRequest,
    BitbucketPipelineIngestResponse,
    BitbucketPipelineListResponse,
    BitbucketPullRequestIngestRequest,
    BitbucketPullRequestIngestResponse,
    BitbucketPullRequestListResponse,
    BitbucketRepositoryIngestRequest,
    BitbucketRepositoryIngestResponse,
    BitbucketRepositoryListResponse,
)
from apso_backend.db.session import get_db_session
from apso_backend.schemas.jira import (
    JiraIssueIngestRequest,
    JiraIssueIngestResponse,
    JiraIssueSearchRequest,
    JiraIssueSearchResponse,
)
from apso_backend.security.context import RequestContext, get_request_context, require_min_role
from apso_backend.services.jira_ingestion import JiraIngestionService
from apso_backend.services.bitbucket_ingestion import BitbucketIngestionService
from apso_backend.services.audit import AuditService

router = APIRouter()


@router.get("", response_model=list[IntegrationSummary])
def list_integrations() -> list[IntegrationSummary]:
    return [
        JiraClient.from_settings().summary(),
        BitbucketClient.from_settings().summary(),
        AwsMockConnector.from_settings().summary(),
    ]


@router.get("/jira/scopes")
def jira_scopes() -> dict[str, list[str]]:
    return {
        "required_now": ["read:account", "read:jira-work"],
        "backlog_only": ["manage:jira-webhook", "write:jira-work"],
        "mvp_policy": ["read_only", "scheduled_polling_first", "no_write_back"],
    }


@router.get("/jira/check")
async def check_jira_connection() -> dict:
    return await JiraClient.from_settings().check_connection()


@router.get("/bitbucket/scopes")
def bitbucket_scopes() -> dict[str, list[str]]:
    return {
        "required_now": BITBUCKET_REQUIRED_READ_SCOPES,
        "optional_diagnostics": BITBUCKET_OPTIONAL_READ_SCOPES,
        "do_not_select_for_mvp": BITBUCKET_SCOPE_EXCLUSIONS,
        "mvp_policy": ["read_only", "scheduled_polling_first", "no_write_back"],
    }


@router.get("/bitbucket/check")
async def check_bitbucket_connection() -> dict:
    return await BitbucketClient.from_settings().check_connection()


@router.get("/bitbucket/repositories", response_model=BitbucketRepositoryListResponse)
async def list_bitbucket_repositories(
    context: RequestContext = Depends(get_request_context),
) -> BitbucketRepositoryListResponse:
    del context
    client = BitbucketClient.from_settings()
    try:
        payload = await client.list_repositories()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    repositories = [normalize_repository(repo) for repo in payload.get("values", [])]
    return BitbucketRepositoryListResponse(repositories=repositories)


@router.get(
    "/bitbucket/repositories/{repo_slug}/pull-requests",
    response_model=BitbucketPullRequestListResponse,
)
async def list_bitbucket_pull_requests(
    repo_slug: str,
    state: str = "OPEN",
    context: RequestContext = Depends(get_request_context),
) -> BitbucketPullRequestListResponse:
    del context
    client = BitbucketClient.from_settings()
    try:
        payload = await client.list_pull_requests(repo_slug=repo_slug, state=state)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    pull_requests = [normalize_pull_request(pr) for pr in payload.get("values", [])]
    return BitbucketPullRequestListResponse(pull_requests=pull_requests)


@router.get(
    "/bitbucket/repositories/{repo_slug}/commits",
    response_model=BitbucketCommitListResponse,
)
async def list_bitbucket_commits(
    repo_slug: str,
    branch: str = "develop",
    context: RequestContext = Depends(get_request_context),
) -> BitbucketCommitListResponse:
    del context
    client = BitbucketClient.from_settings()
    try:
        payload = await client.list_commits(repo_slug=repo_slug, branch=branch)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    commits = [normalize_commit(commit, branch=branch) for commit in payload.get("values", [])]
    return BitbucketCommitListResponse(commits=commits)


@router.get(
    "/bitbucket/repositories/{repo_slug}/pipelines",
    response_model=BitbucketPipelineListResponse,
)
async def list_bitbucket_pipelines(
    repo_slug: str,
    context: RequestContext = Depends(get_request_context),
) -> BitbucketPipelineListResponse:
    del context
    client = BitbucketClient.from_settings()
    try:
        payload = await client.list_pipelines(repo_slug=repo_slug)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    pipelines = [normalize_pipeline(pipeline) for pipeline in payload.get("values", [])]
    return BitbucketPipelineListResponse(pipelines=pipelines)


@router.post("/bitbucket/repositories/ingest", response_model=BitbucketRepositoryIngestResponse)
async def ingest_bitbucket_repositories(
    request: BitbucketRepositoryIngestRequest,
    context: RequestContext = Depends(require_min_role("lead")),
    session: Session = Depends(get_db_session),
) -> BitbucketRepositoryIngestResponse:
    service = BitbucketIngestionService(session)
    try:
        result = await service.ingest_repositories(
            tenant_id=context.tenant_id,
            project_id=request.project_id,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    AuditService(session).record(
        context=context,
        action="bitbucket.repositories_ingested",
        resource_type="bitbucket_repository",
        metadata={"received": result.received, "upserted": result.upserted},
        commit=True,
    )
    return BitbucketRepositoryIngestResponse.model_validate(result.model_dump())


@router.post(
    "/bitbucket/repositories/{repo_slug}/pull-requests/ingest",
    response_model=BitbucketPullRequestIngestResponse,
)
async def ingest_bitbucket_pull_requests(
    repo_slug: str,
    request: BitbucketPullRequestIngestRequest,
    context: RequestContext = Depends(require_min_role("lead")),
    session: Session = Depends(get_db_session),
) -> BitbucketPullRequestIngestResponse:
    service = BitbucketIngestionService(session)
    try:
        result = await service.ingest_pull_requests(
            tenant_id=context.tenant_id,
            repository_id=request.repository_id,
            repo_slug=repo_slug,
            state=request.state,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    AuditService(session).record(
        context=context,
        action="bitbucket.pull_requests_ingested",
        resource_type="bitbucket_pull_request",
        resource_id=repo_slug,
        metadata={"received": result.received, "upserted": result.upserted, "state": request.state},
        commit=True,
    )
    return BitbucketPullRequestIngestResponse.model_validate(result.model_dump())


@router.post(
    "/bitbucket/repositories/{repo_slug}/commits/ingest",
    response_model=BitbucketCommitIngestResponse,
)
async def ingest_bitbucket_commits(
    repo_slug: str,
    request: BitbucketCommitIngestRequest,
    context: RequestContext = Depends(require_min_role("lead")),
    session: Session = Depends(get_db_session),
) -> BitbucketCommitIngestResponse:
    service = BitbucketIngestionService(session)
    try:
        result = await service.ingest_commits(
            tenant_id=context.tenant_id,
            repository_id=request.repository_id,
            repo_slug=repo_slug,
            branch=request.branch,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    AuditService(session).record(
        context=context,
        action="bitbucket.commits_ingested",
        resource_type="bitbucket_commit",
        resource_id=repo_slug,
        metadata={"received": result.received, "upserted": result.upserted, "branch": request.branch},
        commit=True,
    )
    return BitbucketCommitIngestResponse.model_validate(result.model_dump())


@router.post(
    "/bitbucket/repositories/{repo_slug}/pipelines/ingest",
    response_model=BitbucketPipelineIngestResponse,
)
async def ingest_bitbucket_pipelines(
    repo_slug: str,
    request: BitbucketPipelineIngestRequest,
    context: RequestContext = Depends(require_min_role("lead")),
    session: Session = Depends(get_db_session),
) -> BitbucketPipelineIngestResponse:
    service = BitbucketIngestionService(session)
    try:
        result = await service.ingest_pipelines(
            tenant_id=context.tenant_id,
            repository_id=request.repository_id,
            repo_slug=repo_slug,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    AuditService(session).record(
        context=context,
        action="bitbucket.pipelines_ingested",
        resource_type="bitbucket_pipeline",
        resource_id=repo_slug,
        metadata={"received": result.received, "upserted": result.upserted},
        commit=True,
    )
    return BitbucketPipelineIngestResponse.model_validate(result.model_dump())


@router.post("/jira/issues/search", response_model=JiraIssueSearchResponse)
async def search_jira_issues(
    request: JiraIssueSearchRequest,
    context: RequestContext = Depends(get_request_context),
) -> JiraIssueSearchResponse:
    del context
    client = JiraClient.from_settings()
    try:
        payload = await client.search_issues(jql=request.jql, max_results=request.max_results)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    total, max_results, issues = normalize_search_response(payload, client.settings)
    return JiraIssueSearchResponse(total=total, max_results=max_results, issues=issues)


@router.get("/jira/issues/sample-jql")
def jira_sample_jql() -> dict[str, str]:
    return {
        "recent_updated": "updated >= -14d ORDER BY updated DESC",
        "stories_and_bugs": "issuetype in (Story, Bug, Task) ORDER BY updated DESC",
        "project_placeholder": "project = YOUR_PROJECT_KEY ORDER BY updated DESC",
    }


@router.post("/jira/issues/ingest", response_model=JiraIssueIngestResponse)
async def ingest_jira_issues(
    request: JiraIssueIngestRequest,
    context: RequestContext = Depends(require_min_role("lead")),
    session: Session = Depends(get_db_session),
) -> JiraIssueIngestResponse:
    service = JiraIngestionService(session)
    try:
        result = await service.search_and_ingest(
            tenant_id=context.tenant_id,
            project_id=request.project_id,
            jql=request.jql,
            max_results=request.max_results,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    AuditService(session).record(
        context=context,
        action="jira.issues_ingested",
        resource_type="jira_issue",
        metadata={"received": result.received, "upserted": result.upserted, "jql": request.jql},
        commit=True,
    )
    return JiraIssueIngestResponse.model_validate(result.model_dump())

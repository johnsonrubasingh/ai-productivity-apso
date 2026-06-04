from pydantic import BaseModel
from sqlalchemy.orm import Session

from apso_backend.integrations.bitbucket.client import BitbucketClient
from apso_backend.integrations.bitbucket.normalizer import (
    normalize_commit,
    normalize_pipeline,
    normalize_pull_request,
    normalize_repository,
)
from apso_backend.repositories.bitbucket import BitbucketRepository
from apso_backend.schemas.bitbucket import (
    BitbucketCommitSummary,
    BitbucketPipelineSummary,
    BitbucketPullRequestSummary,
    BitbucketRepositorySummary,
)


class BitbucketRepositoryIngestionResult(BaseModel):
    received: int
    upserted: int
    repositories: list[BitbucketRepositorySummary]
    read_only: bool = True


class BitbucketPullRequestIngestionResult(BaseModel):
    received: int
    upserted: int
    pull_requests: list[BitbucketPullRequestSummary]
    read_only: bool = True


class BitbucketCommitIngestionResult(BaseModel):
    received: int
    upserted: int
    commits: list[BitbucketCommitSummary]
    read_only: bool = True


class BitbucketPipelineIngestionResult(BaseModel):
    received: int
    upserted: int
    pipelines: list[BitbucketPipelineSummary]
    read_only: bool = True


class BitbucketIngestionService:
    def __init__(self, session: Session):
        self.session = session

    async def ingest_repositories(
        self,
        *,
        tenant_id: str,
        project_id: str | None,
    ) -> BitbucketRepositoryIngestionResult:
        client = BitbucketClient.from_settings()
        payload = await client.list_repositories()
        raw_repos = payload.get("values", [])
        normalized = [normalize_repository(repo) for repo in raw_repos]
        repo_store = BitbucketRepository(self.session)
        for raw_repo, repo in zip(raw_repos, normalized, strict=False):
            repo_store.upsert_repository(
                tenant_id=tenant_id,
                project_id=project_id,
                workspace=client.settings.workspace,
                repo=repo,
                raw_payload=raw_repo,
            )
        self.session.commit()
        return BitbucketRepositoryIngestionResult(
            received=len(raw_repos),
            upserted=len(normalized),
            repositories=normalized,
        )

    async def ingest_pull_requests(
        self,
        *,
        tenant_id: str,
        repository_id: str | None,
        repo_slug: str,
        state: str = "OPEN",
    ) -> BitbucketPullRequestIngestionResult:
        client = BitbucketClient.from_settings()
        payload = await client.list_pull_requests(repo_slug=repo_slug, state=state)
        raw_prs = payload.get("values", [])
        normalized = [normalize_pull_request(pr) for pr in raw_prs]
        repo_store = BitbucketRepository(self.session)
        for raw_pr, pull_request in zip(raw_prs, normalized, strict=False):
            repo_store.upsert_pull_request(
                tenant_id=tenant_id,
                repository_id=repository_id,
                pull_request=pull_request,
                raw_payload=raw_pr,
            )
        self.session.commit()
        return BitbucketPullRequestIngestionResult(
            received=len(raw_prs),
            upserted=len(normalized),
            pull_requests=normalized,
        )

    async def ingest_commits(
        self,
        *,
        tenant_id: str,
        repository_id: str | None,
        repo_slug: str,
        branch: str = "develop",
    ) -> BitbucketCommitIngestionResult:
        client = BitbucketClient.from_settings()
        payload = await client.list_commits(repo_slug=repo_slug, branch=branch)
        raw_commits = payload.get("values", [])
        normalized = [normalize_commit(commit, branch=branch) for commit in raw_commits]
        repo_store = BitbucketRepository(self.session)
        for raw_commit, commit in zip(raw_commits, normalized, strict=False):
            repo_store.upsert_commit(
                tenant_id=tenant_id,
                repository_id=repository_id,
                commit=commit,
                raw_payload=raw_commit,
            )
        self.session.commit()
        return BitbucketCommitIngestionResult(
            received=len(raw_commits),
            upserted=len(normalized),
            commits=normalized,
        )

    async def ingest_pipelines(
        self,
        *,
        tenant_id: str,
        repository_id: str | None,
        repo_slug: str,
    ) -> BitbucketPipelineIngestionResult:
        client = BitbucketClient.from_settings()
        payload = await client.list_pipelines(repo_slug=repo_slug)
        raw_pipelines = payload.get("values", [])
        normalized = [normalize_pipeline(pipeline) for pipeline in raw_pipelines]
        repo_store = BitbucketRepository(self.session)
        for raw_pipeline, pipeline in zip(raw_pipelines, normalized, strict=False):
            repo_store.upsert_pipeline(
                tenant_id=tenant_id,
                repository_id=repository_id,
                pipeline=pipeline,
                raw_payload=raw_pipeline,
            )
        self.session.commit()
        return BitbucketPipelineIngestionResult(
            received=len(raw_pipelines),
            upserted=len(normalized),
            pipelines=normalized,
        )

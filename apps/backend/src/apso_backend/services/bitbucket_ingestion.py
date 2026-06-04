from pydantic import BaseModel
from sqlalchemy.orm import Session

from apso_backend.integrations.bitbucket.client import BitbucketClient
from apso_backend.integrations.bitbucket.normalizer import (
    normalize_diff_evidence,
    normalize_commit,
    normalize_pipeline,
    normalize_pipeline_step,
    normalize_pull_request,
    normalize_repository,
    normalize_source_evidence,
    normalize_source_file,
    normalize_test_report,
)
from apso_backend.repositories.bitbucket import BitbucketRepository
from apso_backend.schemas.bitbucket import (
    BitbucketCommitSummary,
    BitbucketCodeEvidenceSummary,
    BitbucketPipelineSummary,
    BitbucketPullRequestSummary,
    BitbucketRepositorySummary,
    BitbucketSourceFileSummary,
    BitbucketTestRunSummary,
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


class BitbucketTestRunIngestionResult(BaseModel):
    received: int
    upserted: int
    test_runs: list[BitbucketTestRunSummary]
    read_only: bool = True


class BitbucketCodeEvidenceIngestionResult(BaseModel):
    received: int
    upserted: int
    evidence: list[BitbucketCodeEvidenceSummary]
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

    async def list_pipeline_steps(
        self,
        *,
        repo_slug: str,
        pipeline_uuid: str,
    ) -> list:
        client = BitbucketClient.from_settings()
        payload = await client.list_pipeline_steps(repo_slug=repo_slug, pipeline_uuid=pipeline_uuid)
        return [normalize_pipeline_step(step) for step in payload.get("values", [])]

    async def ingest_pipeline_tests(
        self,
        *,
        tenant_id: str,
        repository_id: str | None,
        repo_slug: str,
        pipeline_uuid: str,
        step_uuid: str | None = None,
    ) -> BitbucketTestRunIngestionResult:
        client = BitbucketClient.from_settings()
        step_uuids = [step_uuid] if step_uuid else [
            step.uuid for step in await self.list_pipeline_steps(repo_slug=repo_slug, pipeline_uuid=pipeline_uuid)
        ]
        repo_store = BitbucketRepository(self.session)
        normalized: list[BitbucketTestRunSummary] = []
        raw_reports: list[dict] = []
        for current_step_uuid in step_uuids:
            if not current_step_uuid:
                continue
            report = await client.get_pipeline_step_test_report(
                repo_slug=repo_slug,
                pipeline_uuid=pipeline_uuid,
                step_uuid=current_step_uuid,
            )
            test_run = normalize_test_report(
                report,
                pipeline_uuid=pipeline_uuid,
                step_uuid=current_step_uuid,
            )
            normalized.append(test_run)
            raw_reports.append(report)
            repo_store.upsert_test_run(
                tenant_id=tenant_id,
                repository_id=repository_id,
                test_run=test_run,
                raw_payload=report,
            )
        self.session.commit()
        return BitbucketTestRunIngestionResult(
            received=len(raw_reports),
            upserted=len(normalized),
            test_runs=normalized,
        )

    async def list_source_files(
        self,
        *,
        repo_slug: str,
        branch: str,
        path: str = "",
        max_files: int = 100,
    ) -> list[BitbucketSourceFileSummary]:
        client = BitbucketClient.from_settings()
        payload = await client.list_source_files(repo_slug=repo_slug, branch=branch, path=path)
        files = []
        for node in payload.get("values", []):
            source_file = normalize_source_file(node)
            if source_file is not None:
                files.append(source_file)
            if len(files) >= max_files:
                break
        return files

    async def ingest_source_evidence(
        self,
        *,
        tenant_id: str,
        repository_id: str | None,
        repo_slug: str,
        branch: str,
        path: str = "",
        max_files: int = 100,
    ) -> BitbucketCodeEvidenceIngestionResult:
        client = BitbucketClient.from_settings()
        repo_store = BitbucketRepository(self.session)
        source_files = await self.list_source_files(
            repo_slug=repo_slug,
            branch=branch,
            path=path,
            max_files=max_files,
        )
        evidence_items: list[BitbucketCodeEvidenceSummary] = []
        for source_file in source_files:
            content = await client.get_source_file(repo_slug=repo_slug, branch=branch, path=source_file.path)
            evidence = normalize_source_evidence(
                source_file,
                branch=branch,
                content_excerpt=content[:8000],
            )
            evidence_items.append(evidence)
            repo_store.upsert_code_evidence(
                tenant_id=tenant_id,
                repository_id=repository_id,
                evidence=evidence,
                raw_payload=source_file.model_dump(),
            )
        self.session.commit()
        return BitbucketCodeEvidenceIngestionResult(
            received=len(source_files),
            upserted=len(evidence_items),
            evidence=evidence_items,
        )

    async def ingest_diff_evidence(
        self,
        *,
        tenant_id: str,
        repository_id: str | None,
        repo_slug: str,
        pull_request_id: int | None = None,
        commit_hash: str | None = None,
    ) -> BitbucketCodeEvidenceIngestionResult:
        client = BitbucketClient.from_settings()
        if pull_request_id is None and commit_hash is None:
            raise RuntimeError("Either pull_request_id or commit_hash is required")
        if pull_request_id is not None:
            diff = await client.get_pull_request_diff(repo_slug=repo_slug, pull_request_id=pull_request_id)
            reference = f"pull_request_diff:{repo_slug}:{pull_request_id}"
        else:
            diff = await client.get_commit_diff(repo_slug=repo_slug, commit_hash=str(commit_hash))
            reference = f"commit_diff:{repo_slug}:{commit_hash}"
        evidence = normalize_diff_evidence(reference=reference, diff_text=diff)
        BitbucketRepository(self.session).upsert_code_evidence(
            tenant_id=tenant_id,
            repository_id=repository_id,
            evidence=evidence,
            raw_payload={"reference": reference},
        )
        self.session.commit()
        return BitbucketCodeEvidenceIngestionResult(received=1, upserted=1, evidence=[evidence])

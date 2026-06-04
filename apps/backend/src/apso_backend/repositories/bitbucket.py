from sqlalchemy import select
from sqlalchemy.orm import Session

from apso_backend.db.models import BitbucketTestRun, CodeEvidence, Commit, PipelineRun, PullRequest, Repository
from apso_backend.schemas.bitbucket import (
    BitbucketCodeEvidenceSummary,
    BitbucketPipelineSummary,
    BitbucketCommitSummary,
    BitbucketPullRequestSummary,
    BitbucketRepositorySummary,
    BitbucketTestRunSummary,
)


class BitbucketRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert_repository(
        self,
        *,
        tenant_id: str,
        project_id: str | None,
        workspace: str,
        repo: BitbucketRepositorySummary,
        raw_payload: dict,
    ) -> Repository:
        existing = self.session.scalar(
            select(Repository).where(
                Repository.tenant_id == tenant_id,
                Repository.provider == "bitbucket",
                Repository.slug == repo.slug,
            )
        )
        if existing is None:
            existing = Repository(
                tenant_id=tenant_id,
                project_id=project_id,
                provider="bitbucket",
                workspace=workspace,
                slug=repo.slug,
                default_branch=repo.main_branch or "develop",
                clone_url=repo.source_url,
                raw_payload=raw_payload,
            )
            self.session.add(existing)
        else:
            existing.project_id = project_id
            existing.workspace = workspace
            existing.default_branch = repo.main_branch or existing.default_branch
            existing.clone_url = repo.source_url
            existing.raw_payload = raw_payload
        return existing

    def upsert_pull_request(
        self,
        *,
        tenant_id: str,
        repository_id: str | None,
        pull_request: BitbucketPullRequestSummary,
        raw_payload: dict,
    ) -> PullRequest:
        existing = self.session.scalar(
            select(PullRequest).where(
                PullRequest.tenant_id == tenant_id,
                PullRequest.repository_id == repository_id,
                PullRequest.external_id == str(pull_request.id),
            )
        )
        if existing is None:
            existing = PullRequest(
                tenant_id=tenant_id,
                repository_id=repository_id,
                external_id=str(pull_request.id),
                title=pull_request.title,
                state=pull_request.state,
                source_branch=pull_request.source_branch,
                target_branch=pull_request.target_branch,
                author=pull_request.author,
                raw_payload=raw_payload,
            )
            self.session.add(existing)
        else:
            existing.title = pull_request.title
            existing.state = pull_request.state
            existing.source_branch = pull_request.source_branch
            existing.target_branch = pull_request.target_branch
            existing.author = pull_request.author
            existing.raw_payload = raw_payload
        return existing

    def upsert_commit(
        self,
        *,
        tenant_id: str,
        repository_id: str | None,
        commit: BitbucketCommitSummary,
        raw_payload: dict,
    ) -> Commit:
        existing = self.session.scalar(
            select(Commit).where(
                Commit.tenant_id == tenant_id,
                Commit.repository_id == repository_id,
                Commit.hash == commit.hash,
            )
        )
        if existing is None:
            existing = Commit(
                tenant_id=tenant_id,
                repository_id=repository_id,
                hash=commit.hash,
                message=commit.message,
                author=commit.author,
                branch=commit.branch,
                committed_at=commit.committed_at,
                raw_payload=raw_payload,
            )
            self.session.add(existing)
        else:
            existing.message = commit.message
            existing.author = commit.author
            existing.branch = commit.branch
            existing.committed_at = commit.committed_at
            existing.raw_payload = raw_payload
        return existing

    def upsert_pipeline(
        self,
        *,
        tenant_id: str,
        repository_id: str | None,
        pipeline: BitbucketPipelineSummary,
        raw_payload: dict,
    ) -> PipelineRun:
        existing = self.session.scalar(
            select(PipelineRun).where(
                PipelineRun.tenant_id == tenant_id,
                PipelineRun.repository_id == repository_id,
                PipelineRun.external_id == pipeline.uuid,
            )
        )
        if existing is None:
            existing = PipelineRun(
                tenant_id=tenant_id,
                repository_id=repository_id,
                external_id=pipeline.uuid,
                provider="bitbucket",
                status=pipeline.result or pipeline.state,
                branch=pipeline.branch,
                commit_sha=pipeline.commit_sha,
                raw_payload=raw_payload,
            )
            self.session.add(existing)
        else:
            existing.status = pipeline.result or pipeline.state
            existing.branch = pipeline.branch
            existing.commit_sha = pipeline.commit_sha
            existing.raw_payload = raw_payload
        return existing

    def upsert_test_run(
        self,
        *,
        tenant_id: str,
        repository_id: str | None,
        test_run: BitbucketTestRunSummary,
        raw_payload: dict,
    ) -> BitbucketTestRun:
        external_id = f"{test_run.pipeline_uuid}:{test_run.step_uuid}"
        existing = self.session.scalar(
            select(BitbucketTestRun).where(
                BitbucketTestRun.tenant_id == tenant_id,
                BitbucketTestRun.external_id == external_id,
            )
        )
        if existing is None:
            existing = BitbucketTestRun(
                tenant_id=tenant_id,
                repository_id=repository_id,
                pipeline_uuid=test_run.pipeline_uuid,
                step_uuid=test_run.step_uuid,
                external_id=external_id,
                total_tests=test_run.total_tests,
                passed_tests=test_run.passed_tests,
                failed_tests=test_run.failed_tests,
                skipped_tests=test_run.skipped_tests,
                duration_seconds=test_run.duration_seconds,
                raw_payload=raw_payload,
            )
            self.session.add(existing)
        else:
            existing.repository_id = repository_id
            existing.total_tests = test_run.total_tests
            existing.passed_tests = test_run.passed_tests
            existing.failed_tests = test_run.failed_tests
            existing.skipped_tests = test_run.skipped_tests
            existing.duration_seconds = test_run.duration_seconds
            existing.raw_payload = raw_payload
        return existing

    def upsert_code_evidence(
        self,
        *,
        tenant_id: str,
        repository_id: str | None,
        evidence: BitbucketCodeEvidenceSummary,
        raw_payload: dict,
    ) -> CodeEvidence:
        existing = self.session.scalar(
            select(CodeEvidence).where(
                CodeEvidence.tenant_id == tenant_id,
                CodeEvidence.provider == "bitbucket",
                CodeEvidence.reference == evidence.reference,
            )
        )
        if existing is None:
            existing = CodeEvidence(
                tenant_id=tenant_id,
                repository_id=repository_id,
                provider="bitbucket",
                evidence_type=evidence.evidence_type,
                reference=evidence.reference,
                file_path=evidence.file_path,
                commit_sha=evidence.commit_sha,
                content_excerpt=evidence.content_excerpt,
                raw_payload=raw_payload,
            )
            self.session.add(existing)
        else:
            existing.repository_id = repository_id
            existing.evidence_type = evidence.evidence_type
            existing.file_path = evidence.file_path
            existing.commit_sha = evidence.commit_sha
            existing.content_excerpt = evidence.content_excerpt
            existing.raw_payload = raw_payload
        return existing

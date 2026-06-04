from pydantic import BaseModel


class BitbucketRepositoryIngestRequest(BaseModel):
    project_id: str | None = None


class BitbucketPullRequestIngestRequest(BaseModel):
    repository_id: str | None = None
    state: str = "OPEN"


class BitbucketPipelineIngestRequest(BaseModel):
    repository_id: str | None = None


class BitbucketPipelineTestIngestRequest(BaseModel):
    repository_id: str | None = None
    pipeline_uuid: str
    step_uuid: str | None = None


class BitbucketSourceEvidenceIngestRequest(BaseModel):
    repository_id: str | None = None
    branch: str = "develop"
    path: str = ""
    max_files: int = 100


class BitbucketDiffEvidenceIngestRequest(BaseModel):
    repository_id: str | None = None
    pull_request_id: int | None = None
    commit_hash: str | None = None


class BitbucketRepositorySummary(BaseModel):
    uuid: str | None = None
    slug: str
    name: str
    full_name: str
    main_branch: str | None = None
    is_private: bool | None = None
    source_url: str | None = None


class BitbucketPullRequestSummary(BaseModel):
    id: int
    title: str
    state: str
    author: str | None = None
    source_branch: str | None = None
    target_branch: str | None = None
    source_url: str | None = None


class BitbucketCommitSummary(BaseModel):
    hash: str
    message: str | None = None
    author: str | None = None
    branch: str | None = None
    committed_at: str | None = None
    source_url: str | None = None


class BitbucketPipelineSummary(BaseModel):
    uuid: str
    state: str
    result: str | None = None
    branch: str | None = None
    commit_sha: str | None = None
    source_url: str | None = None


class BitbucketPipelineStepSummary(BaseModel):
    uuid: str
    name: str | None = None
    state: str | None = None
    result: str | None = None
    started_on: str | None = None
    completed_on: str | None = None


class BitbucketTestRunSummary(BaseModel):
    pipeline_uuid: str
    step_uuid: str
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    duration_seconds: int | None = None
    source_url: str | None = None


class BitbucketSourceFileSummary(BaseModel):
    path: str
    commit_sha: str | None = None
    size: int | None = None
    source_url: str | None = None


class BitbucketCodeEvidenceSummary(BaseModel):
    evidence_type: str
    reference: str
    file_path: str | None = None
    commit_sha: str | None = None
    content_excerpt: str | None = None
    source_url: str | None = None


class BitbucketRepositoryListResponse(BaseModel):
    repositories: list[BitbucketRepositorySummary]
    read_only: bool = True


class BitbucketPullRequestListResponse(BaseModel):
    pull_requests: list[BitbucketPullRequestSummary]
    read_only: bool = True


class BitbucketPipelineListResponse(BaseModel):
    pipelines: list[BitbucketPipelineSummary]
    read_only: bool = True


class BitbucketCommitListResponse(BaseModel):
    commits: list[BitbucketCommitSummary]
    read_only: bool = True


class BitbucketPipelineStepListResponse(BaseModel):
    steps: list[BitbucketPipelineStepSummary]
    read_only: bool = True


class BitbucketTestRunListResponse(BaseModel):
    test_runs: list[BitbucketTestRunSummary]
    read_only: bool = True


class BitbucketSourceFileListResponse(BaseModel):
    files: list[BitbucketSourceFileSummary]
    read_only: bool = True


class BitbucketCodeEvidenceListResponse(BaseModel):
    evidence: list[BitbucketCodeEvidenceSummary]
    read_only: bool = True


class BitbucketRepositoryIngestResponse(BaseModel):
    received: int
    upserted: int
    repositories: list[BitbucketRepositorySummary]
    read_only: bool = True


class BitbucketPullRequestIngestResponse(BaseModel):
    received: int
    upserted: int
    pull_requests: list[BitbucketPullRequestSummary]
    read_only: bool = True


class BitbucketCommitIngestRequest(BaseModel):
    repository_id: str | None = None
    branch: str = "develop"


class BitbucketCommitIngestResponse(BaseModel):
    received: int
    upserted: int
    commits: list[BitbucketCommitSummary]
    read_only: bool = True


class BitbucketPipelineIngestResponse(BaseModel):
    received: int
    upserted: int
    pipelines: list[BitbucketPipelineSummary]
    read_only: bool = True


class BitbucketPipelineTestIngestResponse(BaseModel):
    received: int
    upserted: int
    test_runs: list[BitbucketTestRunSummary]
    read_only: bool = True


class BitbucketCodeEvidenceIngestResponse(BaseModel):
    received: int
    upserted: int
    evidence: list[BitbucketCodeEvidenceSummary]
    read_only: bool = True

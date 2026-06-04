from typing import Literal

from pydantic import BaseModel, Field


JobName = Literal[
    "jira_ingest",
    "bitbucket_repo_ingest",
    "bitbucket_test_ingest",
    "bitbucket_source_evidence_ingest",
    "bitbucket_diff_evidence_ingest",
    "definition_gap_analysis",
    "release_readiness_assessment",
]


class JobRunRequest(BaseModel):
    job_name: JobName
    payload: dict = Field(default_factory=dict)


class JobRunResponse(BaseModel):
    job_name: JobName
    status: Literal["accepted", "completed", "failed"]
    mode: Literal["synchronous_dev", "temporal_pending"]
    result: dict = Field(default_factory=dict)
    note: str

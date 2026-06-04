from sqlalchemy.orm import Session

from apso_backend.ai.schemas import RequirementGapInput
from apso_backend.schemas.jobs import JobRunRequest, JobRunResponse
from apso_backend.schemas.release import ReleaseReadinessRequest
from apso_backend.security.context import RequestContext
from apso_backend.services.bitbucket_ingestion import BitbucketIngestionService
from apso_backend.services.definition_gap import DefinitionGapService
from apso_backend.services.jira_ingestion import JiraIngestionService
from apso_backend.services.release_readiness import ReleaseReadinessService


class JobRunnerService:
    def __init__(self, session: Session | None = None):
        self.session = session

    async def run(self, *, request: JobRunRequest, context: RequestContext) -> JobRunResponse:
        if request.job_name == "definition_gap_analysis":
            payload = RequirementGapInput.model_validate(request.payload)
            result = await DefinitionGapService(session=self.session).analyze(
                payload,
                use_llm=bool(request.payload.get("use_llm", False)),
                persist=bool(request.payload.get("persist", False)),
            )
            return self._completed(request, result.model_dump())

        if request.job_name == "release_readiness_assessment":
            payload = ReleaseReadinessRequest.model_validate(request.payload)
            result = ReleaseReadinessService().assess(payload)
            return self._completed(request, result.model_dump())

        if self.session is None:
            return JobRunResponse(
                job_name=request.job_name,
                status="failed",
                mode="synchronous_dev",
                result={},
                note="Database is not configured for ingestion job execution.",
            )

        if request.job_name == "jira_ingest":
            result = await JiraIngestionService(self.session).search_and_ingest(
                tenant_id=context.tenant_id,
                project_id=request.payload.get("project_id"),
                jql=request.payload["jql"],
                max_results=int(request.payload.get("max_results", 25)),
            )
            return self._completed(request, result.model_dump())

        if request.job_name == "bitbucket_repo_ingest":
            result = await BitbucketIngestionService(self.session).ingest_repositories(
                tenant_id=context.tenant_id,
                project_id=request.payload.get("project_id"),
            )
            return self._completed(request, result.model_dump())

        return JobRunResponse(
            job_name=request.job_name,
            status="failed",
            mode="synchronous_dev",
            result={},
            note="Unknown job name.",
        )

    @staticmethod
    def _completed(request: JobRunRequest, result: dict) -> JobRunResponse:
        return JobRunResponse(
            job_name=request.job_name,
            status="completed",
            mode="synchronous_dev",
            result=result,
            note="Executed synchronously in backend dev mode. Temporal worker execution will use the same service contract.",
        )


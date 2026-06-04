from apso_backend.schemas.release import ReleaseReadinessRequest, ReleaseReadinessResponse


class ReleaseReadinessService:
    def assess(self, request: ReleaseReadinessRequest) -> ReleaseReadinessResponse:
        blockers: list[str] = []
        score = 100

        if request.open_high_risk_findings:
            score -= min(40, request.open_high_risk_findings * 10)
            blockers.append(f"{request.open_high_risk_findings} high-risk findings remain open")
        if request.failed_pipeline_runs:
            score -= min(30, request.failed_pipeline_runs * 10)
            blockers.append(f"{request.failed_pipeline_runs} pipeline runs failed")
        if request.stories_without_tests:
            score -= min(20, request.stories_without_tests * 5)
            blockers.append(f"{request.stories_without_tests} stories lack test evidence")
        if request.unresolved_requirement_gaps:
            score -= min(20, request.unresolved_requirement_gaps * 5)
            blockers.append(f"{request.unresolved_requirement_gaps} requirement gaps remain unresolved")

        score = max(0, score)
        status = "ready" if score >= 85 and not blockers else "needs_review" if score >= 60 else "not_ready"
        return ReleaseReadinessResponse(
            release_name=request.release_name,
            readiness_score=score,
            status=status,
            blockers=blockers,
        )


from apso_backend.schemas.coverage import CoverageGap, CoverageVerificationRequest, CoverageVerificationResponse


class CoverageVerificationService:
    def verify(self, request: CoverageVerificationRequest) -> CoverageVerificationResponse:
        score = 100
        gaps: list[CoverageGap] = []

        if request.linked_commits == 0:
            score -= 25
            gaps.append(
                CoverageGap(
                    gap_type="missing_code_link",
                    severity="high",
                    description="No linked commits were provided for this work item.",
                    recommendation="Link commits or PRs to the Jira item before marking the story release-ready.",
                )
            )

        if request.linked_pull_requests == 0:
            score -= 20
            gaps.append(
                CoverageGap(
                    gap_type="missing_pr_link",
                    severity="medium",
                    description="No pull request evidence was provided for this work item.",
                    recommendation="Ensure implementation changes are reviewed through pull requests and linked to the work item.",
                )
            )

        if request.linked_test_runs == 0:
            score -= 25
            gaps.append(
                CoverageGap(
                    gap_type="missing_test_evidence",
                    severity="high",
                    description="No test run evidence was provided for this work item.",
                    recommendation="Add unit, integration, or acceptance test evidence before release.",
                )
            )

        if request.successful_pipeline_runs == 0:
            score -= 20
            gaps.append(
                CoverageGap(
                    gap_type="missing_successful_pipeline",
                    severity="high",
                    description="No successful pipeline evidence was provided.",
                    recommendation="Confirm the linked code was built and validated by CI/CD.",
                )
            )

        if request.coverage_percent is not None and request.coverage_percent < 70:
            score -= 10
            gaps.append(
                CoverageGap(
                    gap_type="low_test_coverage",
                    severity="medium",
                    description=f"Coverage is {request.coverage_percent:.1f}%, below the default 70% signal threshold.",
                    recommendation="Review coverage gaps and add tests for changed behavior.",
                )
            )

        return CoverageVerificationResponse(
            work_item_key=request.work_item_key,
            coverage_confidence_score=max(0, score),
            gaps=gaps,
        )

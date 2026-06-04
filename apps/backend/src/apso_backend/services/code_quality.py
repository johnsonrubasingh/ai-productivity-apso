from apso_backend.schemas.code_quality import (
    CodeQualityAnalyzeRequest,
    CodeQualityAnalyzeResponse,
    CodeQualityScoreBreakdown,
)
from apso_backend.schemas.scanners import ScannerRunRequest
from apso_backend.services.scanners import ScannerService


class CodeQualityService:
    def analyze(self, request: CodeQualityAnalyzeRequest) -> CodeQualityAnalyzeResponse:
        scanner_service = ScannerService()
        all_findings = []
        for scanner in request.scanners:
            scanner_request = ScannerRunRequest(
                repository_slug=request.repository_slug,
                branch=request.branch,
                scanner=scanner,
                dry_run=not request.execute_scanners,
            )
            if request.execute_scanners and request.repository_path:
                response = scanner_service.execute(scanner_request, repository_path=request.repository_path)
            else:
                response = scanner_service.dry_run(scanner_request)
            all_findings.extend(response.findings)

        breakdown = CodeQualityScoreBreakdown(
            critical=sum(1 for finding in all_findings if finding.severity == "critical"),
            high=sum(1 for finding in all_findings if finding.severity == "high"),
            medium=sum(1 for finding in all_findings if finding.severity == "medium"),
            low=sum(1 for finding in all_findings if finding.severity == "low"),
        )
        score = max(
            0,
            100
            - breakdown.critical * 30
            - breakdown.high * 20
            - breakdown.medium * 10
            - breakdown.low * 3,
        )
        return CodeQualityAnalyzeResponse(
            repository_slug=request.repository_slug,
            branch=request.branch,
            quality_score=score,
            breakdown=breakdown,
            findings=all_findings,
            evidence_policy=(
                "Code quality scores are based on deterministic scanner evidence. "
                "LLM explanations may be added later but must not replace scanner evidence."
            ),
        )

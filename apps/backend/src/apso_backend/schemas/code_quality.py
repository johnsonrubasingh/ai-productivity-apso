from pydantic import BaseModel, Field

from apso_backend.schemas.scanners import ScannerFinding, ScannerName


class CodeQualityAnalyzeRequest(BaseModel):
    repository_slug: str
    branch: str = "develop"
    scanners: list[ScannerName] = Field(default_factory=lambda: ["semgrep", "gitleaks", "trivy"])
    repository_path: str | None = None
    execute_scanners: bool = False


class CodeQualityScoreBreakdown(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class CodeQualityAnalyzeResponse(BaseModel):
    repository_slug: str
    branch: str
    quality_score: int = Field(ge=0, le=100)
    breakdown: CodeQualityScoreBreakdown
    findings: list[ScannerFinding]
    evidence_policy: str
    read_only: bool = True


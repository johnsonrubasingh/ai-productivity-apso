from typing import Literal

from pydantic import BaseModel, Field


ScannerName = Literal["semgrep", "tree_sitter", "gitleaks", "trivy", "owasp_dependency_check"]


class ScannerDefinition(BaseModel):
    name: ScannerName
    purpose: str
    enabled_for_mvp: bool = True
    requires_external_service: bool = False


class ScannerRunRequest(BaseModel):
    repository_slug: str
    branch: str = "develop"
    scanner: ScannerName
    dry_run: bool = True


class ScannerFinding(BaseModel):
    scanner: ScannerName
    severity: Literal["low", "medium", "high", "critical"]
    title: str
    file_path: str | None = None
    line: int | None = None
    evidence: str


class ScannerRunResponse(BaseModel):
    repository_slug: str
    branch: str
    scanner: ScannerName
    dry_run: bool
    tool_available: bool = False
    command: list[str] = Field(default_factory=list)
    return_code: int | None = None
    findings: list[ScannerFinding] = Field(default_factory=list)
    note: str

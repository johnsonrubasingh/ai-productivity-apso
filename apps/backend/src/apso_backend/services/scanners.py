import shutil

from apso_backend.schemas.scanners import ScannerDefinition, ScannerRunRequest, ScannerRunResponse
from apso_backend.services.command_runner import CommandRunner
from apso_backend.services.scanner_parsers import parse_scanner_output


SCANNER_DEFINITIONS = [
    ScannerDefinition(
        name="semgrep",
        purpose="Static analysis for security, correctness, framework misuse, and maintainability rules.",
    ),
    ScannerDefinition(
        name="tree_sitter",
        purpose="Language-aware parsing for symbols, functions, classes, imports, and code chunks.",
    ),
    ScannerDefinition(
        name="gitleaks",
        purpose="Secret detection for committed tokens, passwords, keys, and credentials.",
    ),
    ScannerDefinition(
        name="trivy",
        purpose="Dependency, container, and IaC vulnerability/misconfiguration scanning.",
    ),
    ScannerDefinition(
        name="owasp_dependency_check",
        purpose="Software composition analysis for dependency vulnerability evidence.",
    ),
]


class ScannerService:
    def definitions(self) -> list[ScannerDefinition]:
        return SCANNER_DEFINITIONS

    def dry_run(self, request: ScannerRunRequest) -> ScannerRunResponse:
        command = self._command_for(request)
        tool_available = bool(command and shutil.which(command[0]))
        return ScannerRunResponse(
            repository_slug=request.repository_slug,
            branch=request.branch,
            scanner=request.scanner,
            dry_run=True,
            tool_available=tool_available,
            command=command,
            findings=[],
            note=(
                "Scanner execution is scaffolded. CLI execution will be wired after repository "
                "checkout storage and scanner config files are added."
            ),
        )

    def execute(self, request: ScannerRunRequest, *, repository_path: str) -> ScannerRunResponse:
        command = self._command_for(request)
        if not command:
            return ScannerRunResponse(
                repository_slug=request.repository_slug,
                branch=request.branch,
                scanner=request.scanner,
                dry_run=False,
                command=[],
                note="Scanner command is not configured.",
            )
        if not shutil.which(command[0]):
            return ScannerRunResponse(
                repository_slug=request.repository_slug,
                branch=request.branch,
                scanner=request.scanner,
                dry_run=False,
                tool_available=False,
                command=command,
                note=f"Scanner executable '{command[0]}' is not installed or not on PATH.",
            )
        result = CommandRunner().run(command, cwd=repository_path)
        findings = parse_scanner_output(request.scanner, result.stdout)
        return ScannerRunResponse(
            repository_slug=request.repository_slug,
            branch=request.branch,
            scanner=request.scanner,
            dry_run=False,
            tool_available=True,
            command=command,
            return_code=result.return_code,
            findings=findings,
            note="Scanner command executed. Parser integration will normalize findings in the next implementation slice.",
        )

    def _command_for(self, request: ScannerRunRequest) -> list[str]:
        if request.scanner == "semgrep":
            return ["semgrep", "scan", "--json", "."]
        if request.scanner == "gitleaks":
            return ["gitleaks", "detect", "--no-git", "--redact", "--report-format", "json"]
        if request.scanner == "trivy":
            return ["trivy", "fs", "--format", "json", "."]
        if request.scanner == "owasp_dependency_check":
            return ["dependency-check", "--scan", ".", "--format", "JSON"]
        if request.scanner == "tree_sitter":
            return ["tree-sitter", "parse", "."]
        return []

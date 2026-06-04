import json
from typing import Any

from apso_backend.schemas.scanners import ScannerFinding, ScannerName


def parse_scanner_output(scanner: ScannerName, stdout: str) -> list[ScannerFinding]:
    if not stdout.strip():
        return []
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return [
            ScannerFinding(
                scanner=scanner,
                severity="low",
                title="Scanner returned non-JSON output",
                evidence=stdout[:1000],
            )
        ]

    if scanner == "semgrep":
        return _parse_semgrep(payload)
    if scanner == "gitleaks":
        return _parse_gitleaks(payload)
    if scanner == "trivy":
        return _parse_trivy(payload)
    if scanner == "owasp_dependency_check":
        return _parse_dependency_check(payload)
    return []


def _severity(value: str | None) -> str:
    lowered = (value or "").lower()
    if lowered in {"critical", "high", "medium", "low"}:
        return lowered
    if lowered in {"error"}:
        return "high"
    if lowered in {"warning", "warn"}:
        return "medium"
    return "low"


def _parse_semgrep(payload: dict[str, Any]) -> list[ScannerFinding]:
    findings = []
    for result in payload.get("results", []):
        extra = result.get("extra", {})
        metadata = extra.get("metadata", {})
        findings.append(
            ScannerFinding(
                scanner="semgrep",
                severity=_severity(extra.get("severity") or metadata.get("impact")),
                title=extra.get("message") or result.get("check_id", "Semgrep finding"),
                file_path=result.get("path"),
                line=(result.get("start") or {}).get("line"),
                evidence=result.get("check_id", "semgrep"),
            )
        )
    return findings


def _parse_gitleaks(payload: Any) -> list[ScannerFinding]:
    if isinstance(payload, dict):
        items = payload.get("findings", [])
    else:
        items = payload if isinstance(payload, list) else []
    return [
        ScannerFinding(
            scanner="gitleaks",
            severity="critical",
            title=item.get("Description") or item.get("RuleID") or "Secret detected",
            file_path=item.get("File"),
            line=item.get("StartLine"),
            evidence=item.get("RuleID") or "gitleaks",
        )
        for item in items
    ]


def _parse_trivy(payload: dict[str, Any]) -> list[ScannerFinding]:
    findings = []
    for result in payload.get("Results", []):
        target = result.get("Target")
        for vuln in result.get("Vulnerabilities", []):
            findings.append(
                ScannerFinding(
                    scanner="trivy",
                    severity=_severity(vuln.get("Severity")),
                    title=f"{vuln.get('VulnerabilityID', 'Vulnerability')} in {vuln.get('PkgName', 'package')}",
                    file_path=target,
                    evidence=vuln.get("Title") or vuln.get("Description", "")[:500] or "trivy",
                )
            )
        for misconfig in result.get("Misconfigurations", []):
            findings.append(
                ScannerFinding(
                    scanner="trivy",
                    severity=_severity(misconfig.get("Severity")),
                    title=misconfig.get("Title") or misconfig.get("ID") or "Misconfiguration",
                    file_path=target,
                    evidence=misconfig.get("Message") or misconfig.get("ID", "trivy"),
                )
            )
    return findings


def _parse_dependency_check(payload: dict[str, Any]) -> list[ScannerFinding]:
    findings = []
    for dependency in payload.get("dependencies", []):
        file_name = dependency.get("fileName") or dependency.get("filePath")
        for vuln in dependency.get("vulnerabilities", []):
            findings.append(
                ScannerFinding(
                    scanner="owasp_dependency_check",
                    severity=_severity(vuln.get("severity")),
                    title=f"{vuln.get('name', 'Dependency vulnerability')} in {file_name or 'dependency'}",
                    file_path=file_name,
                    evidence=vuln.get("description", "")[:500] or vuln.get("name", "dependency-check"),
                )
            )
    return findings

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
SECRET_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"ATATT[0-9A-Za-z_\-=]+",
        r"sb_secret_[0-9A-Za-z_\-]+",
        r"eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+",
        r"postgresql://postgres:(?!\$)[^@\s]+@",
    ]
]
IGNORED_PARTS = {"node_modules", ".next", "__pycache__", ".git"}
INTENTIONAL_PATTERN_FILES = {
    ".gitleaks.toml",
    ".semgrep.yml",
    "dependency-check-suppression.xml",
    "scripts/quality/production_readiness_check.py",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def iter_source_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in {".pyc", ".docx", ".pdf", ".png", ".jpg", ".jpeg", ".zip"}:
            continue
        files.append(path)
    return files


def check_no_raw_secrets() -> None:
    for path in iter_source_files():
        relative = path.relative_to(ROOT).as_posix()
        if relative in INTENTIONAL_PATTERN_FILES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                fail(f"possible raw secret found in {path.relative_to(ROOT)}")


def check_locked_environments() -> None:
    env_files = sorted((ROOT / "config").glob("environments.*.yaml"))
    names = {path.name for path in env_files}
    if names != {"environments.dev.yaml", "environments.prod.yaml"}:
        fail(f"only dev/prod environment files are allowed, found {sorted(names)}")

    for path in env_files:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        environment = payload.get("environment")
        if environment not in {"dev", "prod"}:
            fail(f"{path.name} has invalid environment {environment!r}")
        integrations = payload.get("integrations", {})
        for key in ["jira", "bitbucket"]:
            mode = integrations.get(key, {}).get("mode")
            if mode not in {"live_read_only", "mock"}:
                fail(f"{path.name} {key} mode must be live_read_only or mock")
        aws_mode = integrations.get("aws", {}).get("mode")
        if aws_mode not in {"mock", "mock_until_credentials_supplied", "live_read_only"}:
            fail(f"{path.name} aws mode is invalid")
        if payload.get("ai", {}).get("external_providers_enabled") is not False:
            fail(f"{path.name} external AI providers must remain disabled for MVP")


def check_openapi_contract() -> None:
    openapi_path = ROOT / "docs" / "api" / "openapi.json"
    if not openapi_path.exists():
        fail("docs/api/openapi.json is missing")
    payload = json.loads(openapi_path.read_text(encoding="utf-8"))
    paths = payload.get("paths", {})
    required = [
        "/api/v1/health",
        "/api/v1/integrations",
        "/api/v1/engines/definition-gap/analyze",
        "/api/v1/engines/code-quality/analyze",
        "/api/v1/engines/coverage/verify",
        "/api/v1/quality/release-readiness",
        "/api/v1/reports/proof-pack",
        "/api/v1/jobs/run",
        "/api/v1/ops/metrics",
    ]
    missing = [path for path in required if path not in paths]
    if missing:
        fail(f"OpenAPI contract missing required paths: {missing}")


def check_security_scanner_wiring() -> None:
    required_files = [
        ".gitleaks.toml",
        ".semgrep.yml",
        ".trivyignore",
        "dependency-check-suppression.xml",
        "scripts/quality/run-security-scans.ps1",
        ".github/workflows/ci.yml",
    ]
    missing = [path for path in required_files if not (ROOT / path).exists()]
    if missing:
        fail(f"security scanner wiring files missing: {missing}")

    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for token in ["gitleaks", "semgrep", "trivy", "Dependency-Check"]:
        if token not in ci:
            fail(f"CI security scan missing {token}")


def main() -> None:
    check_no_raw_secrets()
    check_locked_environments()
    check_openapi_contract()
    check_security_scanner_wiring()
    print("production readiness static checks passed")


if __name__ == "__main__":
    main()

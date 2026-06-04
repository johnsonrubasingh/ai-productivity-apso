# APSO Security Scanning

APSO uses only locked free/open-source security tools for MVP quality gates.

## Tools

- Gitleaks: committed secret detection.
- Semgrep CE: source-code policy checks.
- Trivy: filesystem vulnerability, secret, and misconfiguration scanning.
- OWASP Dependency-Check: dependency vulnerability scanning.

## Local Developer Run

From the workspace root:

```powershell
.\scripts\quality\run-security-scans.ps1
```

Local mode is advisory. If a scanner is not installed, the script reports the
missing tool and continues so developers can still run the normal production
gate on a clean machine.

Strict mode:

```powershell
.\scripts\quality\run-security-scans.ps1 -RequireTools
```

## CI Enforcement

GitHub Actions runs all scanners in strict mode through `.github/workflows/ci.yml`.
Pull requests must pass:

- Backend tests and static readiness checks.
- Frontend lint, typecheck, and build.
- Gitleaks, Semgrep CE, Trivy, and OWASP Dependency-Check.

## Suppression Policy

Suppressions are not allowed casually.

- `.trivyignore` entries require justification and expiry.
- `dependency-check-suppression.xml` entries require justification and expiry.
- Gitleaks allowlists must never hide real credentials.
- Semgrep rules must not be removed to make a failing build pass.

import os
import shutil

from apso_backend.core.config import get_settings
from apso_backend.schemas.ops import ReadinessCheck, ReadinessResponse
from apso_backend.services.scanners import SCANNER_DEFINITIONS, ScannerService
from apso_backend.services.workspace import WorkspaceService


class ReadinessService:
    def check(self) -> ReadinessResponse:
        settings = get_settings()
        checks: list[ReadinessCheck] = []

        checks.append(ReadinessCheck(name="environment", status="ok", detail=settings.environment))
        checks.append(
            ReadinessCheck(
                name="database_config",
                status="ok" if os.getenv(settings.supabase.db_url_env) else "missing",
                detail=settings.supabase.db_url_env,
            )
        )
        checks.append(
            ReadinessCheck(
                name="jwt_secret",
                status="ok" if os.getenv(settings.supabase.jwt_secret_env) else "missing",
                detail=settings.supabase.jwt_secret_env,
            )
        )

        workspace = WorkspaceService()
        for name, path in {
            "repository_root": workspace.repository_root,
            "artifact_root": workspace.artifact_root,
        }.items():
            checks.append(ReadinessCheck(name=name, status="ok", detail=str(path)))

        scanner_service = ScannerService()
        for scanner in SCANNER_DEFINITIONS:
            command = scanner_service._command_for(  # noqa: SLF001 - readiness intentionally introspects command map.
                type("ScannerRequest", (), {"scanner": scanner.name})()
            )
            executable = command[0] if command else ""
            checks.append(
                ReadinessCheck(
                    name=f"scanner:{scanner.name}",
                    status="ok" if executable and shutil.which(executable) else "missing",
                    detail=executable or "no command",
                )
            )

        blocking = [check for check in checks if check.name in {"environment"} and check.status != "ok"]
        return ReadinessResponse(status="ready" if not blocking else "not_ready", checks=checks)


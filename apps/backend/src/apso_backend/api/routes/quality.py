from fastapi import APIRouter, Depends

from apso_backend.schemas.release import ReleaseReadinessRequest, ReleaseReadinessResponse
from apso_backend.schemas.scanners import ScannerDefinition, ScannerRunRequest, ScannerRunResponse
from apso_backend.security.context import RequestContext, get_request_context, require_min_role
from apso_backend.services.release_readiness import ReleaseReadinessService
from apso_backend.services.scanners import ScannerService

router = APIRouter()


@router.get("/scanners", response_model=list[ScannerDefinition])
def list_scanners() -> list[ScannerDefinition]:
    return ScannerService().definitions()


@router.post("/scanners/dry-run", response_model=ScannerRunResponse)
def scanner_dry_run(
    request: ScannerRunRequest,
    context: RequestContext = Depends(require_min_role("developer")),
) -> ScannerRunResponse:
    del context
    return ScannerService().dry_run(request)


@router.post("/release-readiness", response_model=ReleaseReadinessResponse)
def assess_release_readiness(
    request: ReleaseReadinessRequest,
    context: RequestContext = Depends(require_min_role("developer")),
) -> ReleaseReadinessResponse:
    del context
    return ReleaseReadinessService().assess(request)

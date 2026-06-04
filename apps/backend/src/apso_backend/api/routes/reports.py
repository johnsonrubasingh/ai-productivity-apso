from fastapi import APIRouter, Depends

from apso_backend.schemas.reports import ProofPackRequest, ProofPackResponse
from apso_backend.security.context import RequestContext, require_min_role
from apso_backend.services.reports import ProofPackService

router = APIRouter()


@router.post("/proof-pack", response_model=ProofPackResponse)
def generate_proof_pack(
    request: ProofPackRequest,
    context: RequestContext = Depends(require_min_role("developer")),
) -> ProofPackResponse:
    del context
    return ProofPackService().generate(request)

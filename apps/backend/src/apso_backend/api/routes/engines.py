from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apso_backend.db.session import get_optional_db_session
from apso_backend.ai.schemas import RequirementGapInput, RequirementGapOutput
from apso_backend.schemas.code_quality import CodeQualityAnalyzeRequest, CodeQualityAnalyzeResponse
from apso_backend.schemas.coverage import CoverageVerificationRequest, CoverageVerificationResponse
from apso_backend.security.context import RequestContext, get_request_context
from apso_backend.services.code_quality import CodeQualityService
from apso_backend.services.coverage import CoverageVerificationService
from apso_backend.services.definition_gap import DefinitionGapService

router = APIRouter()


@router.post("/definition-gap/analyze", response_model=RequirementGapOutput)
async def analyze_definition_gap(
    request: RequirementGapInput,
    use_llm: bool = False,
    persist: bool = False,
    context: RequestContext = Depends(get_request_context),
    session: Session | None = Depends(get_optional_db_session),
) -> RequirementGapOutput:
    del context
    if persist and session is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Database is not configured; cannot persist analysis")
    return await DefinitionGapService(session=session).analyze(
        request,
        use_llm=use_llm,
        persist=persist,
    )


@router.post("/code-quality/analyze", response_model=CodeQualityAnalyzeResponse)
def analyze_code_quality(
    request: CodeQualityAnalyzeRequest,
    context: RequestContext = Depends(get_request_context),
) -> CodeQualityAnalyzeResponse:
    del context
    return CodeQualityService().analyze(request)


@router.post("/coverage/verify", response_model=CoverageVerificationResponse)
def verify_coverage(
    request: CoverageVerificationRequest,
    context: RequestContext = Depends(get_request_context),
) -> CoverageVerificationResponse:
    del context
    return CoverageVerificationService().verify(request)

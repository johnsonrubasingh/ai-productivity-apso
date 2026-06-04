from apso_backend.schemas.reports import ProofMetric, ProofPackRequest, ProofPackResponse, ProofPackSection


class ProofPackService:
    def generate(self, request: ProofPackRequest) -> ProofPackResponse:
        metrics = []
        if request.include_placeholders:
            metrics = [
                ProofMetric(
                    name="Hours saved",
                    value="TBD",
                    label="placeholder",
                    evidence="Requires approved before/after delivery evidence.",
                ),
                ProofMetric(
                    name="Rework avoided",
                    value="TBD",
                    label="placeholder",
                    evidence="Requires resolved APSO findings mapped to avoided rework cases.",
                ),
                ProofMetric(
                    name="Defects prevented",
                    value="TBD",
                    label="placeholder",
                    evidence="Requires defect records or quality findings validated by the team.",
                ),
            ]

        return ProofPackResponse(
            title=request.title,
            sections=[
                ProofPackSection(
                    title="Executive Summary",
                    summary=(
                        "APSO analyzes SDLC evidence from Jira, Bitbucket, and CI/CD systems to "
                        "identify requirement gaps, quality risks, coverage gaps, and release readiness signals."
                    ),
                    metrics=metrics,
                ),
                ProofPackSection(
                    title="Evidence Policy",
                    summary=(
                        "The proof pack does not invent productivity results. Missing values remain "
                        "labeled as placeholders until actual evidence is supplied."
                    ),
                    metrics=[],
                ),
            ],
        )


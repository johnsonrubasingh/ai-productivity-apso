import json
from time import perf_counter

from sqlalchemy.orm import Session

from apso_backend.ai.gateway import AiGateway
from apso_backend.ai.prompts.definition_gap import PROMPT_VERSION, build_definition_gap_prompt
from apso_backend.ai.schemas import AiFindingOutput, EvidenceRef, RequirementGapInput, RequirementGapOutput
from apso_backend.repositories.findings import AiRunRepository, FindingRepository
from apso_backend.schemas.findings import FindingCreate


AMBIGUOUS_TERMS = (
    "etc",
    "as needed",
    "user friendly",
    "fast",
    "simple",
    "appropriate",
    "proper",
    "seamless",
    "robust",
    "good",
)


class DefinitionGapService:
    def __init__(self, gateway: AiGateway | None = None, session: Session | None = None):
        self.gateway = gateway or AiGateway.from_settings()
        self.session = session

    async def analyze(
        self,
        payload: RequirementGapInput,
        use_llm: bool = False,
        persist: bool = False,
    ) -> RequirementGapOutput:
        started = perf_counter()
        status = "validated"
        if use_llm:
            try:
                output = await self._analyze_with_llm(payload)
            except Exception:
                status = "fallback_rules"
                output = self._analyze_with_rules(payload)
        else:
            status = "rules"
            output = self._analyze_with_rules(payload)

        if persist and self.session is not None:
            latency_ms = int((perf_counter() - started) * 1000)
            ai_run = AiRunRepository(self.session).create(
                tenant_id=payload.tenant_id,
                task_name="requirement_gap_analysis",
                provider=self.gateway.settings.default_provider,
                model_name=self.gateway.settings.chat_model if use_llm else "deterministic_rules",
                prompt_version=PROMPT_VERSION,
                status=status,
                latency_ms=latency_ms,
                validation_result={"quality_score": output.quality_score, "finding_count": len(output.findings)},
            )
            finding_payloads = [
                FindingCreate(
                    ai_run_id=ai_run.id,
                    project_id=payload.project_id,
                    finding_type=finding.finding_type,
                    severity=finding.severity,
                    title=finding.title,
                    description=f"{finding.description}\n\nRecommendation: {finding.recommendation}",
                    evidence=[evidence.model_dump() for evidence in finding.evidence],
                    confidence=finding.confidence,
                )
                for finding in output.findings
            ]
            created = FindingRepository(self.session).bulk_create(
                tenant_id=payload.tenant_id,
                payloads=finding_payloads,
            )
            output.ai_run_id = ai_run.id
            output.finding_ids = [finding.id for finding in created]
        return output

    async def _analyze_with_llm(self, payload: RequirementGapInput) -> RequirementGapOutput:
        prompt = build_definition_gap_prompt(payload)
        response = await self.gateway.provider().generate_json(prompt=prompt)
        raw_text = response.get("response", "{}")
        parsed = json.loads(raw_text)
        return RequirementGapOutput.model_validate(parsed)

    def _analyze_with_rules(self, payload: RequirementGapInput) -> RequirementGapOutput:
        findings: list[AiFindingOutput] = []
        text = " ".join(
            value or ""
            for value in [payload.summary, payload.description, payload.acceptance_criteria, *payload.comments]
        ).lower()

        if not payload.acceptance_criteria or len(payload.acceptance_criteria.strip()) < 30:
            findings.append(
                self._finding(
                    payload,
                    severity="high",
                    title="Acceptance criteria are missing or too thin",
                    description="The story does not provide enough acceptance criteria for engineering and QA to validate completion.",
                    recommendation="Add concrete Given/When/Then scenarios, edge cases, and negative cases before development starts.",
                    evidence_summary="Acceptance criteria field is empty or shorter than the minimum useful threshold.",
                    confidence=90,
                )
            )

        if not any(term in text for term in ("persona", "as a ", "user", "admin", "customer", "operator")):
            findings.append(
                self._finding(
                    payload,
                    severity="medium",
                    title="User/persona context is unclear",
                    description="The story does not clearly identify who needs the capability or which role is affected.",
                    recommendation="State the persona or user role and explain the user goal the story supports.",
                    evidence_summary="No clear persona phrase or user role was detected in the story text.",
                    confidence=75,
                )
            )

        found_ambiguous = [term for term in AMBIGUOUS_TERMS if term in text]
        if found_ambiguous:
            findings.append(
                self._finding(
                    payload,
                    severity="medium",
                    title="Ambiguous language should be clarified",
                    description=f"The story contains ambiguous terms: {', '.join(found_ambiguous[:5])}.",
                    recommendation="Replace subjective wording with measurable conditions, examples, limits, or acceptance tests.",
                    evidence_summary=f"Detected ambiguous terms: {', '.join(found_ambiguous[:5])}.",
                    confidence=70,
                )
            )

        if not any(term in text for term in ("performance", "security", "audit", "accessibility", "availability", "latency")):
            findings.append(
                self._finding(
                    payload,
                    severity="low",
                    title="Non-functional requirements are not stated",
                    description="The story does not mention security, performance, audit, accessibility, availability, or latency expectations.",
                    recommendation="Confirm whether any NFRs apply and document them explicitly when relevant.",
                    evidence_summary="No common NFR keywords were detected in the story text.",
                    confidence=60,
                )
            )

        score = max(0, 100 - (25 * len([f for f in findings if f.severity == "high"])) - (15 * len([f for f in findings if f.severity == "medium"])) - (8 * len([f for f in findings if f.severity == "low"])))
        return RequirementGapOutput(issue_key=payload.issue_key, quality_score=score, findings=findings)

    @staticmethod
    def _finding(
        payload: RequirementGapInput,
        *,
        severity: str,
        title: str,
        description: str,
        recommendation: str,
        evidence_summary: str,
        confidence: int,
    ) -> AiFindingOutput:
        return AiFindingOutput(
            finding_type="definition_gap",
            severity=severity,  # type: ignore[arg-type]
            title=title,
            description=description,
            recommendation=recommendation,
            confidence=confidence,
            metric_label="ai_inferred",
            evidence=[
                EvidenceRef(
                    source="jira",
                    artifact_type="story",
                    artifact_id=payload.issue_key,
                    summary=evidence_summary,
                )
            ],
        )

from dataclasses import dataclass

from apso_backend.ai.schemas import AiTaskDefinition
from apso_backend.ai.providers.ollama import OllamaProvider
from apso_backend.core.config import AiSettings, get_settings


TASK_DESCRIPTIONS = {
    "requirement_gap_analysis": "Analyze Jira stories for ambiguity, missing acceptance criteria, weak persona, missing NFRs, and weak testability.",
    "code_quality_explanation": "Explain deterministic scanner findings in delivery-friendly language with remediation guidance.",
    "coverage_verification": "Check whether a work item has traceable code, PR, test, and pipeline evidence.",
    "release_risk_summary": "Summarize release risk from unresolved findings, pipeline results, test evidence, and story state.",
    "executive_report_generation": "Generate stakeholder-ready report sections from validated findings and evidence.",
}


@dataclass(frozen=True)
class AiGateway:
    settings: AiSettings

    @classmethod
    def from_settings(cls) -> "AiGateway":
        return cls(settings=get_settings().ai)

    def supported_tasks(self) -> list[AiTaskDefinition]:
        return [
            AiTaskDefinition(
                name=name,  # type: ignore[arg-type]
                description=description,
                provider=self.settings.default_provider,
                model=self.settings.chat_model,
                prompt_version="v0.1.0",
            )
            for name, description in TASK_DESCRIPTIONS.items()
        ]

    def provider(self) -> OllamaProvider:
        return OllamaProvider(
            base_url=self.settings.ollama_base_url,
            chat_model=self.settings.chat_model,
            embedding_model=self.settings.embedding_model,
        )

    async def health(self) -> dict:
        if self.settings.default_provider != "ollama":
            raise RuntimeError("Only Ollama provider is enabled in MVP")
        return await self.provider().health()

    async def run_requirement_gap_analysis(self):
        raise NotImplementedError(
            "AI execution will be implemented after the Ollama provider adapter and prompt registry are added."
        )

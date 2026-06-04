from dataclasses import dataclass

from apso_backend.core.config import AwsSettings, get_settings
from apso_backend.schemas.integrations import IntegrationSummary


@dataclass(frozen=True)
class AwsMockConnector:
    settings: AwsSettings

    @classmethod
    def from_settings(cls) -> "AwsMockConnector":
        return cls(settings=get_settings().integrations.aws)

    def summary(self) -> IntegrationSummary:
        return IntegrationSummary(
            provider="aws",
            mode=self.settings.mode,
            status="mocked" if self.settings.mode.startswith("mock") else "configured",
            read_only=True,
            configured=self.settings.mode.startswith("mock"),
            details={
                "codecommit": "mock",
                "codebuild": "mock",
                "codepipeline": "mock",
                "write_back": False,
                "note": "AWS remains mocked until credentials are supplied later.",
            },
        )


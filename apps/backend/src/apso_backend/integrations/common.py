import os
from dataclasses import dataclass

from apso_backend.schemas.integrations import IntegrationSummary


@dataclass(frozen=True)
class SecretReference:
    env_name: str

    @property
    def is_set(self) -> bool:
        return bool(os.getenv(self.env_name))


def read_only_summary(
    provider: str,
    mode: str,
    configured: bool,
    details: dict[str, str | int | bool | list[str]],
) -> IntegrationSummary:
    return IntegrationSummary(
        provider=provider,
        mode=mode,
        status="configured" if configured else "missing_credentials",
        read_only=True,
        configured=configured,
        details=details,
    )


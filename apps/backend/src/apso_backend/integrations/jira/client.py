from dataclasses import dataclass

import httpx

from apso_backend.core.config import JiraSettings, get_settings
from apso_backend.integrations.common import SecretReference, read_only_summary
from apso_backend.schemas.integrations import IntegrationSummary


@dataclass(frozen=True)
class JiraClient:
    settings: JiraSettings

    @classmethod
    def from_settings(cls) -> "JiraClient":
        return cls(settings=get_settings().integrations.jira)

    @property
    def username_ref(self) -> SecretReference:
        return SecretReference(self.settings.username_env)

    @property
    def token_ref(self) -> SecretReference:
        return SecretReference(self.settings.token_env)

    def summary(self) -> IntegrationSummary:
        return read_only_summary(
            provider="jira",
            mode=self.settings.mode,
            configured=self.username_ref.is_set and self.token_ref.is_set,
            details={
                "base_url": self.settings.base_url,
                "username_env": self.settings.username_env,
                "token_env": self.settings.token_env,
                "required_scopes": ["read:account", "read:jira-work"],
                "write_back": False,
            },
        )

    async def search_issues(self, jql: str, max_results: int = 50) -> dict:
        if self.settings.mode != "live_read_only":
            return {"issues": [], "mock": True}

        import os

        username = os.getenv(self.settings.username_env)
        token = os.getenv(self.settings.token_env)
        if not username or not token:
            raise RuntimeError("Jira credentials are not configured")

        url = self.settings.base_url.rstrip("/") + "/rest/api/3/search"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                url,
                params={"jql": jql, "maxResults": max_results},
                auth=(username, token),
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def check_connection(self) -> dict:
        if self.settings.mode != "live_read_only":
            return {"ok": True, "mode": self.settings.mode, "mock": True}

        import os

        username = os.getenv(self.settings.username_env)
        token = os.getenv(self.settings.token_env)
        if not username or not token:
            return {"ok": False, "mode": self.settings.mode, "reason": "missing_credentials"}

        url = self.settings.base_url.rstrip("/") + "/rest/api/3/myself"
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                url,
                auth=(username, token),
                headers={"Accept": "application/json"},
            )
            if response.status_code >= 400:
                return {"ok": False, "mode": self.settings.mode, "status_code": response.status_code}
            data = response.json()
            return {
                "ok": True,
                "mode": self.settings.mode,
                "account_id": data.get("accountId"),
                "display_name": data.get("displayName"),
            }

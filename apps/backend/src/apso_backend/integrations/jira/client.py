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

        return await self._get_json(
            "/rest/api/3/search/jql",
            params={"jql": jql, "maxResults": max_results},
            timeout=30,
        )

    async def check_connection(self) -> dict:
        if self.settings.mode != "live_read_only":
            return {"ok": True, "mode": self.settings.mode, "mock": True}

        if not self._credentials_configured:
            return {"ok": False, "mode": self.settings.mode, "reason": "missing_credentials"}

        try:
            data = await self._get_json("/rest/api/3/myself", timeout=15)
        except httpx.HTTPStatusError as exc:
            return {"ok": False, "mode": self.settings.mode, "status_code": exc.response.status_code}
        return {
            "ok": True,
            "mode": self.settings.mode,
            "account_id": data.get("accountId"),
            "display_name": data.get("displayName"),
        }

    @property
    def _credentials_configured(self) -> bool:
        import os

        return bool(os.getenv(self.settings.username_env) and os.getenv(self.settings.token_env))

    def _credentials(self) -> tuple[str, str]:
        import os

        username = os.getenv(self.settings.username_env)
        token = os.getenv(self.settings.token_env)
        if not username or not token:
            raise RuntimeError("Jira credentials are not configured")
        return username, token

    async def _get_json(self, path: str, *, params: dict | None = None, timeout: int = 30) -> dict:
        username, token = self._credentials()
        base_url = self.settings.base_url.rstrip("/")
        async with httpx.AsyncClient(timeout=timeout) as client:
            direct = await client.get(
                base_url + path,
                params=params,
                auth=(username, token),
                headers={"Accept": "application/json"},
            )
            if direct.status_code != 401:
                direct.raise_for_status()
                return direct.json()

            cloud_id = await self._cloud_id(client)
            gateway = await client.get(
                f"https://api.atlassian.com/ex/jira/{cloud_id}{path}",
                params=params,
                auth=(username, token),
                headers={"Accept": "application/json"},
            )
            gateway.raise_for_status()
            return gateway.json()

    async def _cloud_id(self, client: httpx.AsyncClient) -> str:
        response = await client.get(
            self.settings.base_url.rstrip("/") + "/_edge/tenant_info",
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        cloud_id = response.json().get("cloudId")
        if not cloud_id:
            raise RuntimeError("Jira cloudId could not be resolved")
        return str(cloud_id)

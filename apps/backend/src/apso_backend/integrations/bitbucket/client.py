from dataclasses import dataclass

import httpx

from apso_backend.core.config import BitbucketSettings, get_settings
from apso_backend.integrations.common import SecretReference, read_only_summary
from apso_backend.schemas.integrations import IntegrationSummary


BITBUCKET_REQUIRED_READ_SCOPES = [
    "read:account",
    "read:me",
    "read:user:bitbucket",
    "read:workspace:bitbucket",
    "read:project:bitbucket",
    "read:repository:bitbucket",
    "read:pullrequest:bitbucket",
    "read:pipeline:bitbucket",
    "read:test:bitbucket",
]

BITBUCKET_OPTIONAL_READ_SCOPES = [
    "read:permission:bitbucket",
    "read:webhook:bitbucket",
    "read:issue:bitbucket",
    "read:wiki:bitbucket",
]

BITBUCKET_SCOPE_EXCLUSIONS = [
    "read:gpg-key:bitbucket",
    "read:ssh-key:bitbucket",
    "read:snippet:bitbucket",
    "read:runner:bitbucket",
    "read:package:bitbucket",
    "write:*",
    "admin:*",
    "delete:*",
]


@dataclass(frozen=True)
class BitbucketClient:
    settings: BitbucketSettings

    @classmethod
    def from_settings(cls) -> "BitbucketClient":
        return cls(settings=get_settings().integrations.bitbucket)

    @property
    def username_ref(self) -> SecretReference:
        return SecretReference(self.settings.username_env)

    @property
    def token_ref(self) -> SecretReference:
        return SecretReference(self.settings.token_env)

    def summary(self) -> IntegrationSummary:
        return read_only_summary(
            provider="bitbucket",
            mode=self.settings.mode,
            configured=self.username_ref.is_set and self.token_ref.is_set,
            details={
                "workspace": self.settings.workspace,
                "repositories": [repo.slug for repo in self.settings.repositories],
                "branches": [repo.branch for repo in self.settings.repositories],
                "username_env": self.settings.username_env,
                "token_env": self.settings.token_env,
                "required_scopes": BITBUCKET_REQUIRED_READ_SCOPES,
                "write_back": False,
            },
        )

    async def list_repositories(self) -> dict:
        if self.settings.mode != "live_read_only":
            return {"values": [], "mock": True}

        import os

        username = os.getenv(self.settings.username_env)
        token = os.getenv(self.settings.token_env)
        if not username or not token:
            raise RuntimeError("Bitbucket credentials are not configured")

        url = f"https://api.bitbucket.org/2.0/repositories/{self.settings.workspace}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                url,
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

        url = "https://api.bitbucket.org/2.0/user"
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
                "account_id": data.get("account_id"),
                "display_name": data.get("display_name"),
                "username": data.get("username"),
            }

    async def list_pull_requests(self, repo_slug: str, state: str = "OPEN") -> dict:
        if self.settings.mode != "live_read_only":
            return {"values": [], "mock": True}

        import os

        username = os.getenv(self.settings.username_env)
        token = os.getenv(self.settings.token_env)
        if not username or not token:
            raise RuntimeError("Bitbucket credentials are not configured")

        url = f"https://api.bitbucket.org/2.0/repositories/{self.settings.workspace}/{repo_slug}/pullrequests"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                url,
                params={"state": state},
                auth=(username, token),
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def list_commits(self, repo_slug: str, branch: str = "develop") -> dict:
        if self.settings.mode != "live_read_only":
            return {"values": [], "mock": True}

        import os

        username = os.getenv(self.settings.username_env)
        token = os.getenv(self.settings.token_env)
        if not username or not token:
            raise RuntimeError("Bitbucket credentials are not configured")

        url = f"https://api.bitbucket.org/2.0/repositories/{self.settings.workspace}/{repo_slug}/commits/{branch}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                url,
                auth=(username, token),
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def list_pipelines(self, repo_slug: str) -> dict:
        if self.settings.mode != "live_read_only":
            return {"values": [], "mock": True}

        import os

        username = os.getenv(self.settings.username_env)
        token = os.getenv(self.settings.token_env)
        if not username or not token:
            raise RuntimeError("Bitbucket credentials are not configured")

        url = f"https://api.bitbucket.org/2.0/repositories/{self.settings.workspace}/{repo_slug}/pipelines"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                url,
                auth=(username, token),
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

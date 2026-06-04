import asyncio

from apso_backend.integrations.bitbucket.client import BitbucketClient
from apso_backend.integrations.jira.client import JiraClient


async def main() -> None:
    jira = await JiraClient.from_settings().check_connection()
    bitbucket = await BitbucketClient.from_settings().check_connection()

    print("jira:", _safe_status(jira))
    print("bitbucket:", _safe_status(bitbucket))


def _safe_status(payload: dict) -> dict:
    allowed = {"ok", "mode", "reason", "status_code", "display_name", "username"}
    return {key: value for key, value in payload.items() if key in allowed}


if __name__ == "__main__":
    asyncio.run(main())


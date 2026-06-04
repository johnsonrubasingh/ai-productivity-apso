import os
import shutil

from apso_backend.core.config import get_settings


def main() -> None:
    settings = get_settings()
    checks = {
        "environment": settings.environment in {"dev", "prod"},
        "jira_username": bool(os.getenv(settings.integrations.jira.username_env)),
        "jira_token": bool(os.getenv(settings.integrations.jira.token_env)),
        "bitbucket_username": bool(os.getenv(settings.integrations.bitbucket.username_env)),
        "bitbucket_token": bool(os.getenv(settings.integrations.bitbucket.token_env)),
        "supabase_db_url": bool(os.getenv(settings.supabase.db_url_env)),
        "supabase_jwt_secret": bool(os.getenv(settings.supabase.jwt_secret_env)),
        "alembic_installed": bool(shutil.which("alembic")),
    }
    for name, ok in checks.items():
        print(f"{name}: {'ok' if ok else 'missing'}")


if __name__ == "__main__":
    main()


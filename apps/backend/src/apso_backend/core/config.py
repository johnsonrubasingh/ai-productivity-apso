from functools import lru_cache
import os
from pathlib import Path
import re
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator

from apso_backend.core.env_file import load_env_file


ENV_PLACEHOLDER_PATTERN = re.compile(r"^\$\{([A-Z0-9_]+)\}$")


def _resolve_root_dir() -> Path:
    configured = os.getenv("APSO_ROOT_DIR")
    if configured:
        return Path(configured).resolve()

    for parent in Path(__file__).resolve().parents:
        if (parent / "config").is_dir():
            return parent

    return Path.cwd().resolve()


ROOT_DIR = _resolve_root_dir()
CONFIG_DIR = Path(os.getenv("APSO_CONFIG_DIR", ROOT_DIR / "config")).resolve()


class AppSettings(BaseModel):
    frontend_url: str
    api_url: str
    cors_origins: list[str] = Field(default_factory=list)

    @field_validator("cors_origins")
    @classmethod
    def block_wildcard_cors(cls, value: list[str]) -> list[str]:
        if "*" in value:
            raise ValueError("Wildcard CORS origins are not allowed")
        return value


class JiraSettings(BaseModel):
    mode: Literal["live_read_only", "mock"]
    base_url: str
    username_env: str
    token_env: str

    @field_validator("mode")
    @classmethod
    def enforce_read_only(cls, value: str) -> str:
        if value != "live_read_only" and value != "mock":
            raise ValueError("Jira MVP mode must remain read-only or mock")
        return value


class BitbucketRepositorySettings(BaseModel):
    slug: str
    branch: str = "develop"


class BitbucketSettings(BaseModel):
    mode: Literal["live_read_only", "mock"]
    workspace: str
    username_env: str
    token_env: str
    repositories: list[BitbucketRepositorySettings] = Field(default_factory=list)

    @field_validator("mode")
    @classmethod
    def enforce_read_only(cls, value: str) -> str:
        if value != "live_read_only" and value != "mock":
            raise ValueError("Bitbucket MVP mode must remain read-only or mock")
        return value


class AwsSettings(BaseModel):
    mode: Literal["mock", "mock_until_credentials_supplied", "live_read_only"]


class IntegrationSettings(BaseModel):
    jira: JiraSettings
    bitbucket: BitbucketSettings
    aws: AwsSettings


class SupabaseSettings(BaseModel):
    url: str
    publishable_key_env: str
    anon_key_env: str
    service_role_key_env: str
    db_url_env: str
    jwt_secret_env: str


class AiSettings(BaseModel):
    gateway_url: str
    ollama_base_url: str = "http://localhost:11434"
    external_providers_enabled: bool = False
    default_provider: Literal["ollama"] = "ollama"
    chat_model: str = "qwen2.5-coder:14b"
    embedding_model: str = "qwen3-embedding:4b"

    @field_validator("external_providers_enabled")
    @classmethod
    def block_external_in_mvp(cls, value: bool) -> bool:
        if value:
            raise ValueError("External AI providers are backlog-only for MVP")
        return value


class SecuritySettings(BaseModel):
    rate_limit_requests: int = Field(default=120, ge=1, le=10000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3600)


class StorageSettings(BaseModel):
    provider: Literal["minio"]
    endpoint: str


class WorkflowSettings(BaseModel):
    provider: Literal["temporal"]
    endpoint: str


class CacheSettings(BaseModel):
    provider: Literal["valkey"]
    endpoint: str


class WorkspaceSettings(BaseModel):
    repository_root: str = "runtime/repositories"
    artifact_root: str = "runtime/artifacts"


class Settings(BaseModel):
    environment: Literal["dev", "prod"]
    app: AppSettings
    integrations: IntegrationSettings
    supabase: SupabaseSettings
    ai: AiSettings
    storage: StorageSettings
    workflow: WorkflowSettings
    cache: CacheSettings
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    workspace: WorkspaceSettings = Field(default_factory=WorkspaceSettings)


def _read_environment_name() -> str:
    return os.getenv("APSO_ENV", "dev").lower().strip()


def _expand_env_placeholders(value):
    if isinstance(value, dict):
        return {key: _expand_env_placeholders(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand_env_placeholders(item) for item in value]
    if isinstance(value, str):
        match = ENV_PLACEHOLDER_PATTERN.match(value)
        if not match:
            return value
        name = match.group(1)
        resolved = os.getenv(name)
        if resolved is None:
            raise ValueError(f"Required environment variable is missing: {name}")
        return resolved
    return value


def load_settings(environment: str | None = None) -> Settings:
    env = environment or _read_environment_name()
    if env not in {"dev", "prod"}:
        raise ValueError("APSO_ENV must be either 'dev' or 'prod'")

    load_env_file(ROOT_DIR / f".env.{env}.local")

    path = CONFIG_DIR / f"environments.{env}.yaml"
    with path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file)

    return Settings.model_validate(_expand_env_placeholders(raw))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return load_settings()

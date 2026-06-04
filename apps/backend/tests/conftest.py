import pytest
from fastapi.testclient import TestClient

from apso_backend.core.config import get_settings
from apso_backend.main import app


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

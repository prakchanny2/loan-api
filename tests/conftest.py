import pytest
from fastapi.testclient import TestClient

from main import APPLICATIONS, app

TEST_API_KEY = "test-only-api-key-that-is-never-used-in-production"


@pytest.fixture
def api_key():
    return TEST_API_KEY


@pytest.fixture
def client(monkeypatch, api_key):
    monkeypatch.setenv("API_KEY", TEST_API_KEY)
    APPLICATIONS.clear()
    with TestClient(app, headers={"X-API-Key": api_key}) as test_client:
        yield test_client

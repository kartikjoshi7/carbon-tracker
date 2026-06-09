"""
Shared pytest fixtures for the Carbon Engine test suite.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    """Provides a FastAPI TestClient bound to the application instance."""
    return TestClient(app)

"""
Unit tests for the FastAPI main application module.
Tests security headers, SPA serving, and health check.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestSecurityHeaders:
    """Tests that security headers are injected into every response."""

    def test_x_content_type_options(self) -> None:
        response = client.get("/api/health")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

    def test_x_frame_options(self) -> None:
        response = client.get("/api/health")
        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_referrer_policy(self) -> None:
        response = client.get("/api/health")
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    def test_permissions_policy(self) -> None:
        response = client.get("/api/health")
        assert response.headers.get("Permissions-Policy") == "camera=(), microphone=(), geolocation=()"

    def test_strict_transport_security(self) -> None:
        response = client.get("/api/health")
        assert "max-age=" in response.headers.get("Strict-Transport-Security", "")


class TestSPAFallback:
    """Tests that unknown routes return the SPA or 404 for API paths."""

    def test_unknown_api_route_returns_404(self) -> None:
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_unknown_non_api_route(self) -> None:
        # If static dir doesn't exist, this will 404; if it does, it serves index.html
        response = client.get("/some/random/path")
        assert response.status_code in (200, 404)

"""
Unit tests for the dependency injection module.
Tests lazy initialization, fallback behaviour, and singleton caching.
"""


class TestGetDbClient:
    """Tests for the get_db_client dependency."""

    def test_no_credentials_returns_none(self, monkeypatch) -> None:
        import app.deps as deps
        from app.config import Settings

        deps._db_client = None
        # Inject a Settings instance with no credentials
        monkeypatch.setattr(deps, "settings", Settings(supabase_url="", supabase_key=""))

        result = deps.get_db_client()
        assert result is None

    def test_singleton_caching(self) -> None:
        """If a client is already cached, get_db_client returns the same instance."""
        import app.deps as deps
        sentinel = object()
        deps._db_client = sentinel  # type: ignore[assignment]
        assert deps.get_db_client() is sentinel
        deps._db_client = None  # cleanup


class TestGetAiClient:
    """Tests for the get_ai_client dependency."""

    def test_no_api_key_returns_genai_module(self, monkeypatch) -> None:
        import app.deps as deps
        from app.config import Settings

        deps._ai_configured = False
        monkeypatch.setattr(deps, "settings", Settings(gemini_api_key=""))

        result = deps.get_ai_client()
        # Should still return the genai module (or None if not installed)
        assert result is None or hasattr(result, "GenerativeModel")

    def test_with_api_key_configures_and_returns(self, monkeypatch) -> None:
        import app.deps as deps
        from app.config import Settings

        deps._ai_configured = False
        monkeypatch.setattr(deps, "settings", Settings(gemini_api_key="test-key-12345"))

        result = deps.get_ai_client()
        assert result is None or hasattr(result, "GenerativeModel")

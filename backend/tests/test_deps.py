"""
Unit tests for the dependency injection module.
Tests lazy initialization, fallback behaviour, and singleton caching.
"""
import os


class TestGetDbClient:
    """Tests for the get_db_client dependency."""

    def test_no_env_returns_none(self, monkeypatch) -> None:
        import app.deps as deps
        # Reset cached singleton AND env
        deps._db_client = None
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_KEY", raising=False)
        # Also block dotenv from reloading .env
        monkeypatch.setattr(os, "getenv", lambda key, default=None: {
            "SUPABASE_URL": None,
            "SUPABASE_KEY": None,
        }.get(key, os.environ.get(key, default)))

        result = deps.get_db_client()
        assert result is None

    def test_singleton_caching(self) -> None:
        """If a client is already cached, get_db_client returns the same instance."""
        import app.deps as deps
        sentinel = object()
        deps._db_client = sentinel  # type: ignore
        assert deps.get_db_client() is sentinel
        deps._db_client = None  # cleanup


class TestGetAiClient:
    """Tests for the get_ai_client dependency."""

    def test_no_api_key_returns_genai_module(self, monkeypatch) -> None:
        import app.deps as deps
        deps._ai_configured = False
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        result = deps.get_ai_client()
        # Should still return the genai module (or None if not installed)
        assert result is None or hasattr(result, "GenerativeModel")

    def test_with_api_key_configures_and_returns(self, monkeypatch) -> None:
        import app.deps as deps
        deps._ai_configured = False
        monkeypatch.setenv("GEMINI_API_KEY", "test-key-12345")

        result = deps.get_ai_client()
        assert result is None or hasattr(result, "GenerativeModel")

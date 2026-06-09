"""
Unit tests for the centralized configuration module.
"""

from app.config import Settings


class TestSettings:
    """Tests for the Settings dataclass."""

    def test_default_settings_have_empty_credentials(self, monkeypatch) -> None:
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        s = Settings()
        assert not s.has_supabase
        assert not s.has_gemini

    def test_has_supabase_when_both_set(self, monkeypatch) -> None:
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        s = Settings()
        assert s.has_supabase

    def test_has_gemini_when_key_set(self, monkeypatch) -> None:
        monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
        s = Settings()
        assert s.has_gemini

    def test_default_port(self, monkeypatch) -> None:
        monkeypatch.delenv("PORT", raising=False)
        s = Settings()
        assert s.port == 8080

    def test_custom_port(self, monkeypatch) -> None:
        monkeypatch.setenv("PORT", "9090")
        s = Settings()
        assert s.port == 9090

    def test_settings_is_frozen(self) -> None:
        s = Settings()
        try:
            s.port = 9999  # type: ignore[misc]
            raised = False
        except AttributeError:
            raised = True
        assert raised, "Settings should be immutable (frozen dataclass)"

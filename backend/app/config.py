"""
Centralized application configuration.

All environment variables are read once at import time and validated.
Downstream modules import from here instead of calling ``os.getenv``
directly, ensuring a single source of truth and early failure on
misconfiguration.
"""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv  # type: ignore[import-untyped]

load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable application settings loaded from environment variables."""

    # ── Supabase ────────────────────────────────────────────────────
    supabase_url: str = field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    supabase_key: str = field(default_factory=lambda: os.getenv("SUPABASE_KEY", ""))

    # ── Google Gemini ───────────────────────────────────────────────
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))

    # ── Server ──────────────────────────────────────────────────────
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8080")))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    @property
    def has_supabase(self) -> bool:
        """Return True if Supabase credentials are configured."""
        return bool(self.supabase_url and self.supabase_key)

    @property
    def has_gemini(self) -> bool:
        """Return True if a Gemini API key is configured."""
        return bool(self.gemini_api_key)


# Singleton instance — import this in other modules.
settings = Settings()

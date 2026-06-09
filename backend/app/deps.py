"""
Dependency injection providers for Supabase and Google Gemini clients.

Both clients are lazily initialized as singletons on first request.
If credentials are missing, the providers return ``None``, and the
calling code gracefully degrades to mock data or rule-based fallbacks.
"""

from typing import Any

from supabase import Client, create_client  # type: ignore[import-untyped]

from app.config import settings

_db_client: Client | None = None
_ai_configured: bool = False


def get_db_client() -> Client | None:
    """
    Provide the Supabase client via FastAPI dependency injection.

    Initializes a singleton client on first request to prevent repeated
    connections.  Returns ``None`` when credentials are absent.
    """
    global _db_client
    if _db_client is None and settings.has_supabase:
        _db_client = create_client(settings.supabase_url, settings.supabase_key)
    return _db_client


def get_ai_client() -> Any:
    """
    Provide the Gemini AI client module via FastAPI dependency injection.

    Configures the API key on the first request.  Returns ``None`` when
    the ``google-generativeai`` package is not installed.
    """
    global _ai_configured
    if not _ai_configured and settings.has_gemini:
        try:
            import google.generativeai as genai  # type: ignore[import-untyped]

            genai.configure(api_key=settings.gemini_api_key)
            _ai_configured = True
            return genai
        except ImportError:
            return None
    try:
        import google.generativeai as genai  # type: ignore[import-untyped]

        return genai
    except ImportError:
        return None

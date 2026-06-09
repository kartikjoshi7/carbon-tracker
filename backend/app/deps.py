"""
Dependency injection providers for Supabase and Google Gemini clients.

Both clients are lazily initialized as singletons on first request.
If credentials are missing, the providers return ``None``, and the
calling code gracefully degrades to mock data or rule-based fallbacks.
"""
import os
from typing import Any

from dotenv import load_dotenv  # type: ignore[import-untyped]
from supabase import Client, create_client  # type: ignore[import-untyped]

load_dotenv()

_db_client: Client | None = None
_ai_configured: bool = False

def get_db_client() -> Client | None:
    """
    Dependency to provide the Supabase client.
    Initializes a singleton client on first request to prevent repeated connections.
    """
    global _db_client
    if _db_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if url and key:
            _db_client = create_client(url, key)
    return _db_client

def get_ai_client() -> Any:
    """
    Dependency to provide the Gemini AI client module.
    Configures the API key on the first request.
    """
    global _ai_configured
    if not _ai_configured:
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai  # type: ignore
                genai.configure(api_key=gemini_key)
                _ai_configured = True
                return genai
            except ImportError:
                pass
    try:
        import google.generativeai as genai  # type: ignore
        return genai
    except ImportError:
        return None

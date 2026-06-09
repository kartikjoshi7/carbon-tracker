"""
Unit tests for the eco_concierge service module.
Tests the Gemini AI integration, rule-based fallback, and receipt parsing.
"""


# ── Fallback Generator ──────────────────────────────────────────────

class TestFallbackGenerator:
    """Tests for the static rule-based fallback generator."""

    def test_energy_fallback_contains_co2(self) -> None:
        from app.services.eco_concierge import _fallback_generator
        result = _fallback_generator("energy", 5.0, 6.15)
        assert "6.15" in result
        assert "CO2e" in result

    def test_transit_fallback_contains_co2(self) -> None:
        from app.services.eco_concierge import _fallback_generator
        result = _fallback_generator("transit", 10.0, 1.0)
        assert "1.0" in result

    def test_waste_fallback_contains_grams(self) -> None:
        from app.services.eco_concierge import _fallback_generator
        result = _fallback_generator("waste", 250.0, 0.5)
        assert "250.0" in result
        assert "0.5" in result

    def test_unknown_category_returns_generic(self) -> None:
        from app.services.eco_concierge import _fallback_generator
        result = _fallback_generator("unknown", 1.0, 1.0)
        assert "action" in result.lower() or "green" in result.lower()


# ── Insights Sync (No AI) ──────────────────────────────────────────

class TestGenerateInsightsSync:
    """Tests for generate_insights_sync with no AI client (fallback path)."""

    def test_no_ai_client_uses_fallback(self) -> None:
        from app.services.eco_concierge import generate_insights_sync
        result = generate_insights_sync(ai=None, category="energy", metric_value=5.0, calculated_co2=6.15)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_no_ai_client_transit(self) -> None:
        from app.services.eco_concierge import generate_insights_sync
        result = generate_insights_sync(ai=None, category="transit", metric_value=10.0, calculated_co2=1.0)
        assert "1.0" in result

    def test_no_ai_client_waste(self) -> None:
        from app.services.eco_concierge import generate_insights_sync
        result = generate_insights_sync(ai=None, category="waste", metric_value=200.0, calculated_co2=0.4)
        assert "200.0" in result


# ── Insights Sync (Mocked AI failure) ──────────────────────────────

class TestGenerateInsightsSyncAIFailure:
    """Tests that AI exceptions gracefully fall back."""

    def test_ai_exception_falls_back(self) -> None:
        from app.services.eco_concierge import generate_insights_sync

        class FakeAI:
            class GenerativeModel:
                def __init__(self, name: str):
                    raise RuntimeError("Model not available")

        result = generate_insights_sync(ai=FakeAI(), category="energy", metric_value=5.0, calculated_co2=6.15)
        assert isinstance(result, str)
        assert len(result) > 0


# ── Process Eco Insights (Background Task) ─────────────────────────

class TestProcessEcoInsights:
    """Tests for the background task wrapper."""

    def test_process_without_db_does_not_crash(self) -> None:
        from app.services.eco_concierge import process_eco_insights
        # Should log a warning but not raise
        process_eco_insights(db=None, ai=None, user_id="test", category="energy", metric_value=5.0, calculated_co2=6.15)

    def test_process_with_mock_db_failure(self) -> None:
        from app.services.eco_concierge import process_eco_insights

        class FakeDB:
            def table(self, name: str):
                raise RuntimeError("DB unavailable")

        # Should catch the exception internally and not raise
        process_eco_insights(db=FakeDB(), ai=None, user_id="test", category="transit", metric_value=10.0, calculated_co2=1.0)


# ── Receipt Parsing ─────────────────────────────────────────────────

class TestParseReceiptImage:
    """Tests for the receipt image parser."""

    def test_no_ai_returns_default(self) -> None:
        import asyncio

        from app.services.eco_concierge import parse_receipt_image
        result = asyncio.run(parse_receipt_image(ai=None, file_bytes=b"fake image data"))
        assert result["category"] == "energy"
        assert result["value"] == 150.0

    def test_ai_failure_returns_default(self) -> None:
        import asyncio

        from app.services.eco_concierge import parse_receipt_image

        class FakeAI:
            class GenerativeModel:
                def __init__(self, name: str):
                    raise RuntimeError("Vision not available")

        result = asyncio.run(parse_receipt_image(ai=FakeAI(), file_bytes=b"fake image data"))
        assert result["category"] == "energy"
        assert isinstance(result["value"], float)

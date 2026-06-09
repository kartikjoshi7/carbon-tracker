"""
Unit tests for the eco_concierge service module.
Tests the Gemini AI integration, rule-based fallback, and receipt parsing.
"""
import asyncio
from typing import Any
from unittest.mock import MagicMock

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


# ── Insights Sync (Mocked AI success) ──────────────────────────────

class TestGenerateInsightsSyncAISuccess:
    """Tests that a successful AI response is returned directly."""

    def _build_mock_ai(self, response_text: str) -> Any:
        """Create a mock AI module whose GenerativeModel returns the given text."""
        mock_response = MagicMock()
        mock_response.text = response_text

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        mock_ai = MagicMock()
        mock_ai.GenerativeModel.return_value = mock_model
        return mock_ai

    def test_ai_success_returns_generated_text(self) -> None:
        from app.services.eco_concierge import generate_insights_sync
        mock_ai = self._build_mock_ai("Switch to LED bulbs to save 30% energy.")
        result = generate_insights_sync(ai=mock_ai, category="energy", metric_value=5.0, calculated_co2=6.15)
        assert result == "Switch to LED bulbs to save 30% energy."

    def test_ai_success_strips_whitespace(self) -> None:
        from app.services.eco_concierge import generate_insights_sync
        mock_ai = self._build_mock_ai("  Use public transit.  \n")
        result = generate_insights_sync(ai=mock_ai, category="transit", metric_value=10.0, calculated_co2=1.0)
        assert result == "Use public transit."

    def test_ai_first_model_fails_second_succeeds(self) -> None:
        """When the first model throws, the cascade should try the next."""
        from app.services.eco_concierge import generate_insights_sync

        call_count = 0

        class FakeModel:
            def __init__(self, name: str):
                self.name = name

            def generate_content(self, prompt: str) -> Any:
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise RuntimeError("First model quota exceeded")
                mock_resp = MagicMock()
                mock_resp.text = "Carpool with classmates."
                return mock_resp

        mock_ai = MagicMock()
        mock_ai.GenerativeModel.side_effect = lambda name: FakeModel(name)
        result = generate_insights_sync(ai=mock_ai, category="transit", metric_value=12.0, calculated_co2=0.6)
        assert result == "Carpool with classmates."
        assert call_count == 2


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

    def test_all_models_fail_uses_fallback(self) -> None:
        """When every model in the cascade fails, fallback should trigger."""
        from app.services.eco_concierge import generate_insights_sync

        mock_model = MagicMock()
        mock_model.generate_content.side_effect = RuntimeError("All fail")

        mock_ai = MagicMock()
        mock_ai.GenerativeModel.return_value = mock_model

        result = generate_insights_sync(ai=mock_ai, category="waste", metric_value=300.0, calculated_co2=0.6)
        # Should get fallback text, not crash
        assert "300.0" in result or "action" in result.lower()


# ── Process Eco Insights (Background Task) ─────────────────────────

class TestProcessEcoInsights:
    """Tests for the background task wrapper."""

    def test_process_without_db_does_not_crash(self) -> None:
        from app.services.eco_concierge import process_eco_insights
        process_eco_insights(db=None, ai=None, user_id="test", category="energy", metric_value=5.0, calculated_co2=6.15)

    def test_process_with_mock_db_failure(self) -> None:
        from app.services.eco_concierge import process_eco_insights

        class FakeDB:
            def table(self, name: str) -> None:
                raise RuntimeError("DB unavailable")

        process_eco_insights(db=FakeDB(), ai=None, user_id="test", category="transit", metric_value=10.0, calculated_co2=1.0)

    def test_process_with_mock_db_success(self) -> None:
        """When DB and AI are mocked, the full pipeline should execute."""
        from app.services.eco_concierge import process_eco_insights

        mock_table = MagicMock()
        mock_db = MagicMock()
        mock_db.table.return_value = mock_table

        process_eco_insights(db=mock_db, ai=None, user_id="test", category="energy", metric_value=5.0, calculated_co2=6.15)
        mock_db.table.assert_called_once_with("footprint_insights")


# ── Receipt Parsing ─────────────────────────────────────────────────

class TestParseReceiptImage:
    """Tests for the receipt image parser."""

    def test_no_ai_returns_default(self) -> None:
        from app.services.eco_concierge import parse_receipt_image
        result = asyncio.run(parse_receipt_image(ai=None, file_bytes=b"fake image data"))
        assert result["category"] == "energy"
        assert result["value"] == 150.0

    def test_ai_failure_returns_default(self) -> None:
        from app.services.eco_concierge import parse_receipt_image

        class FakeAI:
            class GenerativeModel:
                def __init__(self, name: str):
                    raise RuntimeError("Vision not available")

        result = asyncio.run(parse_receipt_image(ai=FakeAI(), file_bytes=b"fake image data"))
        assert result["category"] == "energy"
        assert isinstance(result["value"], float)

    def test_successful_vision_parse(self) -> None:
        """Mock a successful Gemini Vision response."""
        from app.services.eco_concierge import parse_receipt_image

        mock_response = MagicMock()
        mock_response.text = '{"category": "transit", "value": 42.5}'

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        mock_ai = MagicMock()
        mock_ai.GenerativeModel.return_value = mock_model

        # Create a minimal valid PNG (1x1 pixel)
        import io

        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (1, 1)).save(buf, format="PNG")
        png_bytes = buf.getvalue()

        result = asyncio.run(parse_receipt_image(ai=mock_ai, file_bytes=png_bytes))
        assert result["category"] == "transit"
        assert result["value"] == 42.5

    def test_vision_strips_json_code_block(self) -> None:
        """Vision response wrapped in ```json block should be cleaned."""
        from app.services.eco_concierge import parse_receipt_image

        mock_response = MagicMock()
        mock_response.text = '```json\n{"category": "energy", "value": 200.0}\n```'

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        mock_ai = MagicMock()
        mock_ai.GenerativeModel.return_value = mock_model

        import io

        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (1, 1)).save(buf, format="PNG")
        png_bytes = buf.getvalue()

        result = asyncio.run(parse_receipt_image(ai=mock_ai, file_bytes=png_bytes))
        assert result["category"] == "energy"
        assert result["value"] == 200.0

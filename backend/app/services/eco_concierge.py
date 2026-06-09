"""
AI-powered eco-concierge and receipt parsing service.

Provides a hybrid insight engine: attempts Google Gemini first, then
falls back to a deterministic rule-based generator so the user always
receives actionable reduction advice — even when offline.
"""

import io
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Gemini Model Cascade ────────────────────────────────────────────
# Ordered list of models to attempt; the first success wins.
_TEXT_MODELS: list[str] = [
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]

_VISION_MODELS: list[str] = [
    "gemini-3.1-flash-image",
    "gemini-2.5-flash-image",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
]

# ── Default receipt fallback ────────────────────────────────────────
_DEFAULT_RECEIPT: dict[str, Any] = {"category": "energy", "value": 150.0}


# ── Insight Generation ──────────────────────────────────────────────

def generate_insights_sync(
    ai: Any, category: str, metric_value: float, calculated_co2: float,
) -> str:
    """
    Generate a personalised reduction tip.

    Uses the Gemini API when available; falls back to a static rule
    engine targeting a university-student persona.
    """
    if not ai:
        return _fallback_generator(category, metric_value, calculated_co2)

    try:
        prompt = (
            "You are an Eco-Concierge tailored to a university student "
            "living in a shared off-campus apartment. "
            f"The user just tracked their carbon footprint for category: {category}. "
            f"Metric value: {metric_value}. Calculated CO2e: {calculated_co2} kg. "
            "Provide a concise, highly tailored, 1-2 sentence actionable tip. "
            "Focus on split utility bills, coordinating shared commutes to "
            "campus, and cafeteria/meal waste if applicable."
        )

        last_error: Exception | None = None
        for model_name in _TEXT_MODELS:
            try:
                model = ai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as exc:
                logger.warning("Model %s failed: %s", model_name, exc)
                last_error = exc

        logger.error("All Gemini text models failed. Last error: %s", last_error)
        return _fallback_generator(category, metric_value, calculated_co2)
    except Exception:
        logger.exception("Error initializing Gemini text service")
        return _fallback_generator(category, metric_value, calculated_co2)


def _fallback_generator(category: str, metric_value: float, calculated_co2: float) -> str:
    """Return a deterministic reduction tip for the given category."""
    tips: dict[str, str] = {
        "energy": (
            f"Talk to your roommates to optimize the split AC usage. "
            f"Saving {calculated_co2}kg CO2e lowers the shared apartment "
            f"electricity bill for everyone."
        ),
        "transit": (
            f"Coordinating a shared commute to campus reduces your per-capita "
            f"emission by {calculated_co2}kg CO2e compared to riding alone!"
        ),
        "waste": (
            f"University cafeteria portions are large. Saving {metric_value}g "
            f"of food lowers waste footprint by {calculated_co2}kg CO2e."
        ),
    }
    return tips.get(category, "Every small action counts towards a greener campus.")


# ── Background Task ─────────────────────────────────────────────────

def process_eco_insights(
    db: Any,
    ai: Any,
    user_id: str,
    category: str,
    metric_value: float,
    calculated_co2: float,
) -> None:
    """
    Background task: generate an insight and persist it to Supabase.

    Called via ``BackgroundTasks.add_task`` so the HTTP response is not
    blocked by AI latency.
    """
    insight = generate_insights_sync(ai, category, metric_value, calculated_co2)

    if not db:
        logger.warning("Supabase client not available, skipping insight persistence.")
        return

    payload = {
        "user_id": user_id,
        "category": category,
        "insight_text": insight,
        "related_co2": calculated_co2,
    }
    try:
        db.table("footprint_insights").insert(payload).execute()
        logger.info("Insight saved for user %s", user_id)
    except Exception:
        logger.exception("Failed to save insight to Supabase")


# ── Receipt Parsing ─────────────────────────────────────────────────

async def parse_receipt_image(ai: Any, file_bytes: bytes) -> dict[str, Any]:
    """
    Extract category and value from an uploaded utility bill.

    Uses Gemini Vision multimodal models.  Returns a default value on
    failure so the user can correct it manually.
    """
    if not ai:
        return dict(_DEFAULT_RECEIPT)

    try:
        from PIL import Image  # type: ignore[import-untyped]

        image = Image.open(io.BytesIO(file_bytes))
        prompt = (
            "Analyze this receipt or bill. Extract the total electricity "
            "usage in kWh (for energy bills) or total distance in km (for "
            "travel receipts). Return ONLY a raw JSON object with keys "
            "'category' (either 'energy' or 'transit') and 'value' (a float). "
            "Do not include markdown code block formatting."
        )

        last_error: Exception | None = None
        for model_name in _VISION_MODELS:
            try:
                model = ai.GenerativeModel(model_name)
                response = model.generate_content([prompt, image])

                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:-3].strip()

                data = json.loads(text)
                return {
                    "category": data.get("category", "energy"),
                    "value": float(data.get("value", 0.0)),
                }
            except Exception as exc:
                logger.warning("Vision model %s failed: %s", model_name, exc)
                last_error = exc

        logger.error("All Gemini vision models failed. Last error: %s", last_error)
        return dict(_DEFAULT_RECEIPT)
    except Exception:
        logger.exception("Error initializing Gemini vision service")
        return dict(_DEFAULT_RECEIPT)

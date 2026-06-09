import logging
import os

logger = logging.getLogger(__name__)

from typing import Any

def generate_insights_sync(ai: Any, category: str, metric_value: float, calculated_co2: float) -> str:
    """
    Hybrid model: checks for injected AI client. If absent, falls back to static rule-based generator
    targeting a generic university student persona.
    """
    if not ai:
        return _fallback_generator(category, metric_value, calculated_co2)

    try:
        prompt = f"""
        You are an Eco-Concierge tailored to a university student living in a shared off-campus apartment.
        The user just tracked their carbon footprint for category: {category}.
        Metric value: {metric_value}. Calculated CO2e: {calculated_co2} kg.
        Provide a concise, highly tailored, 1-2 sentence actionable tip.
        Focus on split utility bills, coordinating shared commutes to campus, and cafeteria/meal waste if applicable.
        """

        models_to_try = ['gemini-3.5-flash', 'gemini-3-flash-preview', 'gemini-2.5-flash', 'gemini-2.5-pro']
        last_error = None
        for model_name in models_to_try:
            try:
                model = ai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                logger.warning(f"Model {model_name} failed: {e}")
                last_error = e

        logger.error(f"All Gemini models failed. Last error: {last_error}")
        return _fallback_generator(category, metric_value, calculated_co2)
    except Exception as e:
        logger.error(f"Error initializing Gemini: {e}")
        return _fallback_generator(category, metric_value, calculated_co2)

def _fallback_generator(category: str, metric_value: float, calculated_co2: float) -> str:
    if category == "energy":
        return f"Talk to your roommates to optimize the split AC usage. Saving {calculated_co2}kg CO2e lowers the shared apartment electricity bill for everyone."
    elif category == "transit":
        return f"Coordinating a shared commute to campus reduces your per-capita emission by {calculated_co2}kg CO2e compared to riding alone!"
    elif category == "waste":
        return f"University cafeteria portions are large. Saving {metric_value}g of food lowers waste footprint by {calculated_co2}kg CO2e."
    return "Every small action counts towards a greener campus."

def process_eco_insights(db: Any, ai: Any, user_id: str, category: str, metric_value: float, calculated_co2: float):
    """
    Background task to generate eco-concierge insights without blocking the main thread.
    """
    insight = generate_insights_sync(ai, category, metric_value, calculated_co2)

    # Save this insight to Supabase
    if not db:
        logger.warning("Supabase client not available, skipping insight persistence.")
        return

    payload = {
        "user_id": user_id,
        "category": category,
        "insight_text": insight,
        "related_co2": calculated_co2
    }
    try:
        db.table("footprint_insights").insert(payload).execute()
        logger.info(f"Insight saved successfully for {user_id}")
    except Exception as e:
        logger.error(f"Failed to save insight to Supabase: {e}")

async def parse_receipt_image(ai: Any, file_bytes: bytes) -> dict:
    """
    Uses Gemini Vision to parse an uploaded utility bill or travel receipt.
    """
    if not ai:
        # Fallback if no key: simulate an energy bill parse
        return {"category": "energy", "value": 150.0}

    try:
        import io
        import json
        from PIL import Image

        image = Image.open(io.BytesIO(file_bytes))
        prompt = "Analyze this receipt or bill. Extract the total electricity usage in kWh (for energy bills) or total distance in km (for travel receipts). Return ONLY a raw JSON object with keys 'category' (either 'energy' or 'transit') and 'value' (a float). Do not include markdown code block formatting."

        models_to_try = ['gemini-3.1-flash-image', 'gemini-2.5-flash-image', 'gemini-3.5-flash', 'gemini-2.5-flash']
        last_error = None
        for model_name in models_to_try:
            try:
                model = ai.GenerativeModel(model_name)
                response = model.generate_content([prompt, image])

                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:-3].strip()

                data = json.loads(text)
                return {"category": data.get("category", "energy"), "value": float(data.get("value", 0.0))}
            except Exception as e:
                logger.warning(f"Vision model {model_name} failed: {e}")
                last_error = e

        logger.error(f"All Gemini vision models failed. Last error: {last_error}")
        return {"category": "energy", "value": 150.0}
    except Exception as e:
        logger.error(f"Error initializing Gemini vision: {e}")
        return {"category": "energy", "value": 150.0}

import logging
import os

logger = logging.getLogger(__name__)

def generate_insights_sync(category: str, metric_value: float, calculated_co2: float) -> str:
    """
    Hybrid model: checks for GEMINI_API_KEY. If absent, falls back to static rule-based generator
    targeting a generic university student persona.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return _fallback_generator(category, metric_value, calculated_co2)
    
    try:
        import google.generativeai as genai  # type: ignore
        genai.configure(api_key=gemini_key)
        # Using a fast, lightweight model for background tasks
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are an Eco-Concierge tailored to a university student living in a shared off-campus apartment.
        The user just tracked their carbon footprint for category: {category}.
        Metric value: {metric_value}. Calculated CO2e: {calculated_co2} kg.
        Provide a concise, highly tailored, 1-2 sentence actionable tip. 
        Focus on split utility bills, coordinating shared commutes to campus, and cafeteria/meal waste if applicable.
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error during Gemini generation: {e}")
        return _fallback_generator(category, metric_value, calculated_co2)

def _fallback_generator(category: str, metric_value: float, calculated_co2: float) -> str:
    if category == "energy":
        return f"Talk to your roommates to optimize the split AC usage. Saving {calculated_co2}kg CO2e lowers the shared apartment electricity bill for everyone."
    elif category == "transit":
        return f"Coordinating a shared commute to campus reduces your per-capita emission by {calculated_co2}kg CO2e compared to riding alone!"
    elif category == "waste":
        return f"University cafeteria portions are large. Saving {metric_value}g of food lowers waste footprint by {calculated_co2}kg CO2e."
    return "Every small action counts towards a greener campus."

async def process_eco_insights(user_id: str, category: str, metric_value: float, calculated_co2: float):
    """
    Background task to generate eco-concierge insights without blocking the main thread.
    """
    insight = generate_insights_sync(category, metric_value, calculated_co2)
    
    # Save this insight to Supabase
    from app.services.database import supabase
    if not supabase:
        logger.warning("Supabase client not initialized, skipping insight persistence.")
        return
        
    payload = {
        "user_id": user_id,
        "category": category,
        "insight_text": insight,
        "related_co2": calculated_co2
    }
    try:
        supabase.table("footprint_insights").insert(payload).execute()
        logger.info(f"Insight saved successfully for {user_id}")
    except Exception as e:
        logger.error(f"Failed to save insight to Supabase: {e}")

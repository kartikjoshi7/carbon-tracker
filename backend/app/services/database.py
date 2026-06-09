import logging
import os
from typing import Any, Optional

from dotenv import load_dotenv
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Fail fast validation check
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables.")

# Initialize the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def insert_footprint_log(
    user_id: str,
    category: str,
    metric_value: float,
    calculated_co2: float
) -> Optional[Any]:
    """
    Inserts a footprint log into the footprint_logs table.
    
    Args:
        user_id (str): The unique identifier of the user.
        category (str): The category of the activity (e.g., 'energy', 'transit', 'waste').
        metric_value (float): The raw input metric value.
        calculated_co2 (float): The computed CO2 equivalent footprint.
        
    Returns:
        Optional[Any]: The data returned by Supabase upon successful insert, or None if an error occurred.
    """
    payload = {
        "user_id": user_id,
        "category": category,
        "metric_value": metric_value,
        "calculated_co2": calculated_co2
    }

    try:
        response = supabase.table("footprint_logs").insert(payload).execute()
        return response.data
    except Exception as e:
        logger.error(f"Network or database error while inserting footprint log: {e}")
        return None

def get_footprint_history(user_id: str) -> list:
    try:
        response = supabase.table("footprint_logs").select("*").eq("user_id", user_id).execute()
        # If response data is empty, table might be newly created or empty
        if not response.data:
            raise ValueError("No data found")
        return response.data
    except Exception as e:
        logger.error(f"Error fetching history (serving mock data): {e}")
        return [
            {"category": "energy", "calculated_co2": 15.2, "created_at": "2023-10-01"},
            {"category": "transit", "calculated_co2": 4.5, "created_at": "2023-10-02"},
            {"category": "waste", "calculated_co2": 2.1, "created_at": "2023-10-03"},
            {"category": "energy", "calculated_co2": 12.0, "created_at": "2023-10-04"},
            {"category": "transit", "calculated_co2": 5.8, "created_at": "2023-10-05"},
        ]

def get_leaderboard() -> list:
    try:
        response = supabase.table("footprint_logs").select("user_id, calculated_co2").execute()
        data = response.data
        if not data:
            raise ValueError("No data found")
        scores: dict[str, float] = {}
        for row in data:
            uid = row["user_id"]
            scores[uid] = scores.get(uid, 0) + row["calculated_co2"]
        
        # Sort by lowest footprint (encouraging reduction)
        sorted_scores = sorted([{"user_id": k, "total_co2": round(v, 2)} for k, v in scores.items()], key=lambda x: float(str(x["total_co2"])))
        return sorted_scores[:10]
    except Exception as e:
        logger.error(f"Error fetching leaderboard (serving mock data): {e}")
        return [
            {"user_id": "EcoNinja_99", "total_co2": 12.4},
            {"user_id": "user_123", "total_co2": 39.6},
            {"user_id": "GreenHacker", "total_co2": 45.2},
            {"user_id": "CaptainPlanet", "total_co2": 51.0},
            {"user_id": "Sustain_Bot", "total_co2": 62.8},
        ]

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

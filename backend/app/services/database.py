"""
Supabase persistence layer for carbon footprint data.

All functions accept an optional ``Client`` parameter via dependency
injection.  When the client is ``None`` (no credentials) or a network
error occurs, representative mock data is returned so that the
application remains fully functional offline.
"""

import logging
from typing import Any

from supabase import Client  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

# ── Table Names ─────────────────────────────────────────────────────
_TABLE_FOOTPRINT_LOGS: str = "footprint_logs"

# ── Mock Data ───────────────────────────────────────────────────────
# Served when Supabase is unavailable, keeping the app usable offline.
_MOCK_HISTORY: list[dict[str, Any]] = [
    {"category": "energy", "calculated_co2": 15.2, "created_at": "2023-10-01"},
    {"category": "transit", "calculated_co2": 4.5, "created_at": "2023-10-02"},
    {"category": "waste", "calculated_co2": 2.1, "created_at": "2023-10-03"},
    {"category": "energy", "calculated_co2": 12.0, "created_at": "2023-10-04"},
    {"category": "transit", "calculated_co2": 5.8, "created_at": "2023-10-05"},
]

_MOCK_LEADERBOARD: list[dict[str, Any]] = [
    {"user_id": "EcoNinja_99", "total_co2": 12.4},
    {"user_id": "GreenUser_42", "total_co2": 39.6},
    {"user_id": "GreenHacker", "total_co2": 45.2},
    {"user_id": "CaptainPlanet", "total_co2": 51.0},
    {"user_id": "Sustain_Bot", "total_co2": 62.8},
]

# Maximum number of users shown on the leaderboard.
_LEADERBOARD_LIMIT: int = 10


# ── Write Operations ───────────────────────────────────────────────

def insert_footprint_log(
    db: Client | None,
    user_id: str,
    category: str,
    metric_value: float,
    calculated_co2: float,
) -> Any | None:
    """
    Insert a footprint snapshot into Supabase.

    Returns:
        The inserted row data on success, or ``None`` on failure.
    """
    payload = {
        "user_id": user_id,
        "category": category,
        "metric_value": metric_value,
        "calculated_co2": calculated_co2,
    }

    try:
        if not db:
            raise ValueError("No database client available.")
        response = db.table(_TABLE_FOOTPRINT_LOGS).insert(payload).execute()
        return response.data
    except Exception:
        logger.exception("Failed to insert footprint log")
        return None


# ── Read Operations ────────────────────────────────────────────────

def get_footprint_history(db: Client | None, user_id: str) -> list[dict[str, Any]]:
    """
    Fetch emission history for a device.

    Returns mock data when Supabase is unavailable or the table is empty.
    """
    try:
        if not db:
            raise ValueError("No database client available.")
        response = (
            db.table(_TABLE_FOOTPRINT_LOGS)
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        if not response.data:
            raise ValueError("No data found")
        return response.data
    except Exception:
        logger.exception("Error fetching history — serving mock data")
        return list(_MOCK_HISTORY)


def get_leaderboard(db: Client | None) -> list[dict[str, Any]]:
    """
    Aggregate and rank all users by lowest total CO₂e.

    Returns mock data when Supabase is unavailable.
    """
    try:
        if not db:
            raise ValueError("No database client available.")
        response = (
            db.table(_TABLE_FOOTPRINT_LOGS)
            .select("user_id, calculated_co2")
            .execute()
        )
        data = response.data
        if not data:
            raise ValueError("No data found")

        scores: dict[str, float] = {}
        for row in data:
            uid: str = row["user_id"]
            scores[uid] = scores.get(uid, 0.0) + row["calculated_co2"]

        ranked: list[dict[str, Any]] = [
            {"user_id": k, "total_co2": round(v, 2)} for k, v in scores.items()
        ]
        ranked.sort(key=lambda entry: entry.get("total_co2", 0.0))  # type: ignore[arg-type]
        return ranked[:_LEADERBOARD_LIMIT]
    except Exception:
        logger.exception("Error fetching leaderboard — serving mock data")
        return list(_MOCK_LEADERBOARD)

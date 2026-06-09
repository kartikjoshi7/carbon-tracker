"""
API routes for carbon footprint tracking.

Each endpoint calculates CO₂e for a specific category, persists the
result to Supabase, and enqueues a background AI insight generation task.
"""
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from supabase import Client

from app.deps import get_ai_client, get_db_client
from app.schemas.footprint import EnergyTrackingRequest, TransitTrackingRequest, WasteTrackingRequest
from app.services.carbon_calc import calculate_energy_co2, calculate_transit_co2, calculate_waste_co2
from app.services.database import get_footprint_history, get_leaderboard, insert_footprint_log
from app.services.eco_concierge import parse_receipt_image, process_eco_insights

router = APIRouter(prefix="/api/v1/footprint", tags=["footprint"])

# ── Constants ───────────────────────────────────────────────────────
# Source: Our World in Data, 2022 — global average per-capita daily CO₂e.
GLOBAL_AVG_DAILY_CO2E_KG: float = 13.7

UNDERSTANDING_CONTEXT: str = (
    f"The global average daily footprint is ~{GLOBAL_AVG_DAILY_CO2E_KG} kg CO2e. "
    "Compare your score to understand your impact."
)

# Map user-facing transport modes to internal calculation keys.
TRANSIT_MODE_MAP: dict[str, str] = {
    "shared_rickshaw": "rickshaw",
    "campus_shuttle": "shuttle",
    "two_wheeler": "two_wheeler",
    "walking": "walking",
}


# ── Tracking Endpoints ─────────────────────────────────────────────

@router.post("/energy")
def track_energy(
    request: EnergyTrackingRequest,
    background_tasks: BackgroundTasks,
    db: Client | None = Depends(get_db_client),
    ai: Any = Depends(get_ai_client),
) -> dict[str, Any]:
    """Calculate and persist energy-related CO₂e emissions."""
    co2 = calculate_energy_co2(
        ac_hours=request.ac_hours_logged,
        roommates=request.roommate_count,
        shared_kwh=request.shared_appliance_kwh,
    )

    insert_footprint_log(db=db, user_id=request.user_id, category="energy",
                         metric_value=request.ac_hours_logged, calculated_co2=co2)

    background_tasks.add_task(
        process_eco_insights, db, ai, request.user_id,
        "energy", request.ac_hours_logged, co2,
    )

    return {
        "calculated_co2": co2,
        "message": "Energy footprint tracked successfully.",
        "understanding_context": UNDERSTANDING_CONTEXT,
    }


@router.post("/transit")
def track_transit(
    request: TransitTrackingRequest,
    background_tasks: BackgroundTasks,
    db: Client | None = Depends(get_db_client),
    ai: Any = Depends(get_ai_client),
) -> dict[str, Any]:
    """Calculate and persist transit-related CO₂e emissions."""
    mapped_mode = TRANSIT_MODE_MAP.get(request.transport_mode, request.transport_mode)

    co2 = calculate_transit_co2(
        distance=request.distance_km,
        mode=mapped_mode,
        passengers=request.passenger_count,
    )

    insert_footprint_log(db=db, user_id=request.user_id, category="transit",
                         metric_value=request.distance_km, calculated_co2=co2)

    background_tasks.add_task(
        process_eco_insights, db, ai, request.user_id,
        "transit", request.distance_km, co2,
    )

    return {
        "calculated_co2": co2,
        "message": "Transit footprint tracked successfully.",
        "understanding_context": UNDERSTANDING_CONTEXT,
    }


@router.post("/waste")
def track_waste(
    request: WasteTrackingRequest,
    background_tasks: BackgroundTasks,
    db: Client | None = Depends(get_db_client),
    ai: Any = Depends(get_ai_client),
) -> dict[str, Any]:
    """Calculate and persist waste-related CO₂e emissions."""
    co2 = calculate_waste_co2(grams=request.estimated_waste_grams)

    insert_footprint_log(db=db, user_id=request.user_id, category="waste",
                         metric_value=request.estimated_waste_grams, calculated_co2=co2)

    background_tasks.add_task(
        process_eco_insights, db, ai, request.user_id,
        "waste", request.estimated_waste_grams, co2,
    )

    return {
        "calculated_co2": co2,
        "message": "Waste footprint tracked successfully.",
        "understanding_context": UNDERSTANDING_CONTEXT,
    }


# ── Read Endpoints ─────────────────────────────────────────────────

@router.get("/history/{user_id}")
def fetch_history(user_id: str, db: Client | None = Depends(get_db_client)) -> dict[str, list]:
    """Retrieve the emission history for an anonymous device."""
    data = get_footprint_history(db, user_id)
    return {"history": data}


@router.get("/leaderboard")
def fetch_leaderboard(db: Client | None = Depends(get_db_client)) -> dict[str, list]:
    """Return the top 10 users ranked by lowest total CO₂e."""
    data = get_leaderboard(db)
    return {"leaderboard": data}


# ── Receipt Parser ─────────────────────────────────────────────────

@router.post("/upload-receipt")
async def upload_receipt(
    file: UploadFile = File(...),
    ai: Any = Depends(get_ai_client),
) -> dict[str, Any]:
    """Extract category and value from an uploaded utility bill via Gemini Vision."""
    contents = await file.read()
    parsed_data = await parse_receipt_image(ai, contents)
    return parsed_data

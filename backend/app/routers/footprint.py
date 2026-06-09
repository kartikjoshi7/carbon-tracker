from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from supabase import Client

from app.deps import get_ai_client, get_db_client
from app.schemas.footprint import EnergyTrackingRequest, TransitTrackingRequest, WasteTrackingRequest
from app.services.carbon_calc import calculate_energy_co2, calculate_transit_co2, calculate_waste_co2
from app.services.database import get_footprint_history, get_leaderboard, insert_footprint_log
from app.services.eco_concierge import parse_receipt_image, process_eco_insights

router = APIRouter(prefix="/api/v1/footprint", tags=["footprint"])


@router.post("/energy")
def track_energy(
    request: EnergyTrackingRequest,
    background_tasks: BackgroundTasks,
    db: Client | None = Depends(get_db_client),
    ai: Any = Depends(get_ai_client)
):
    """
    Endpoint to calculate and track energy-related CO2e emissions.
    """
    co2 = calculate_energy_co2(
        ac_hours=request.ac_hours_logged,
        roommates=request.roommate_count,
        shared_kwh=request.shared_appliance_kwh
    )

    insert_footprint_log(
        db=db,
        user_id=request.user_id,
        category="energy",
        metric_value=request.ac_hours_logged,
        calculated_co2=co2
    )

    # Enqueue AI insight generation to run in the background
    background_tasks.add_task(process_eco_insights, db, ai, request.user_id, "energy", request.ac_hours_logged, co2)

    return {
        "calculated_co2": co2,
        "message": "Energy footprint tracked successfully. AI is generating insights in the background.",
        "understanding_context": "The global average daily footprint is ~13.7 kg CO2e. Compare your score to understand your impact."
    }


@router.post("/transit")
def track_transit(
    request: TransitTrackingRequest,
    background_tasks: BackgroundTasks,
    db: Client | None = Depends(get_db_client),
    ai: Any = Depends(get_ai_client)
):
    """
    Endpoint to calculate and track transit-related CO2e emissions.
    """
    # Map schema mode to mathematical calculation mode
    mode_mapping = {
        "shared_rickshaw": "rickshaw",
        "campus_shuttle": "shuttle",
        "two_wheeler": "two_wheeler",
        "walking": "walking"
    }
    mapped_mode = mode_mapping.get(request.transport_mode, request.transport_mode)

    co2 = calculate_transit_co2(
        distance=request.distance_km,
        mode=mapped_mode,
        passengers=request.passenger_count
    )

    insert_footprint_log(
        db=db,
        user_id=request.user_id,
        category="transit",
        metric_value=request.distance_km,
        calculated_co2=co2
    )

    # Enqueue AI insight generation to run in the background
    background_tasks.add_task(process_eco_insights, db, ai, request.user_id, "transit", request.distance_km, co2)

    return {
        "calculated_co2": co2,
        "message": "Transit footprint tracked successfully. AI is generating insights in the background.",
        "understanding_context": "The global average daily footprint is ~13.7 kg CO2e. Compare your score to understand your impact."
    }


@router.post("/waste")
def track_waste(
    request: WasteTrackingRequest,
    background_tasks: BackgroundTasks,
    db: Client | None = Depends(get_db_client),
    ai: Any = Depends(get_ai_client)
):
    """
    Endpoint to calculate and track waste-related CO2e emissions.
    """
    co2 = calculate_waste_co2(grams=request.estimated_waste_grams)

    insert_footprint_log(
        db=db,
        user_id=request.user_id,
        category="waste",
        metric_value=request.estimated_waste_grams,
        calculated_co2=co2
    )

    # Enqueue AI insight generation to run in the background
    background_tasks.add_task(process_eco_insights, db, ai, request.user_id, "waste", request.estimated_waste_grams, co2)

    return {
        "calculated_co2": co2,
        "message": "Waste footprint tracked successfully. AI is generating insights in the background.",
        "understanding_context": "The global average daily footprint is ~13.7 kg CO2e. Compare your score to understand your impact."
    }

@router.get("/history/{user_id}")
def fetch_history(user_id: str, db: Client | None = Depends(get_db_client)):
    data = get_footprint_history(db, user_id)
    return {"history": data}

@router.get("/leaderboard")
def fetch_leaderboard(db: Client | None = Depends(get_db_client)):
    data = get_leaderboard(db)
    return {"leaderboard": data}

@router.post("/upload-receipt")
async def upload_receipt(
    file: UploadFile = File(...),
    ai: Any = Depends(get_ai_client)
):
    contents = await file.read()
    parsed_data = await parse_receipt_image(ai, contents)
    return parsed_data

from fastapi import APIRouter, BackgroundTasks

from app.schemas.footprint import EnergyTrackingRequest, TransitTrackingRequest, WasteTrackingRequest
from app.services.carbon_calc import calculate_energy_co2, calculate_transit_co2, calculate_waste_co2
from app.services.database import insert_footprint_log
from app.services.eco_concierge import process_eco_insights

router = APIRouter(prefix="/api/v1/footprint", tags=["footprint"])


@router.post("/energy")
async def track_energy(request: EnergyTrackingRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to calculate and track energy-related CO2e emissions.
    """
    co2 = calculate_energy_co2(
        ac_hours=request.ac_hours_logged,
        roommates=request.roommate_count,
        shared_kwh=request.shared_appliance_kwh
    )
    
    insert_footprint_log(
        user_id="user_123",
        category="energy",
        metric_value=request.ac_hours_logged,
        calculated_co2=co2
    )
    
    # Enqueue AI insight generation to run in the background
    background_tasks.add_task(process_eco_insights, "user_123", "energy", request.ac_hours_logged, co2)
    
    return {
        "calculated_co2": co2,
        "message": "Energy footprint tracked successfully. AI is generating insights in the background."
    }


@router.post("/transit")
async def track_transit(request: TransitTrackingRequest, background_tasks: BackgroundTasks):
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
        user_id="user_123",
        category="transit",
        metric_value=request.distance_km,
        calculated_co2=co2
    )
    
    # Enqueue AI insight generation to run in the background
    background_tasks.add_task(process_eco_insights, "user_123", "transit", request.distance_km, co2)
    
    return {
        "calculated_co2": co2,
        "message": "Transit footprint tracked successfully. AI is generating insights in the background."
    }


@router.post("/waste")
async def track_waste(request: WasteTrackingRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to calculate and track waste-related CO2e emissions.
    """
    co2 = calculate_waste_co2(grams=request.estimated_waste_grams)
    
    insert_footprint_log(
        user_id="user_123",
        category="waste",
        metric_value=request.estimated_waste_grams,
        calculated_co2=co2
    )
    
    # Enqueue AI insight generation to run in the background
    background_tasks.add_task(process_eco_insights, "user_123", "waste", request.estimated_waste_grams, co2)
    
    return {
        "calculated_co2": co2,
        "message": "Waste footprint tracked successfully. AI is generating insights in the background."
    }

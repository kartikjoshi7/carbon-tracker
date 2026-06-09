from typing import Literal

from pydantic import BaseModel, Field


class EnergyTrackingRequest(BaseModel):
    """
    Validates logged electricity and cooling data for shared living spaces.
    """
    user_id: str = Field(
        ...,
        description="Anonymous device ID"
    )
    roommate_count: int = Field(
        ...,
        ge=1,
        description="The total number of roommates sharing the living space. Must be at least 1."
    )
    ac_hours_logged: float = Field(
        ...,
        ge=0.0,
        le=24.0,
        description="The number of hours the air conditioning was active. Must be between 0.0 and 24.0."
    )
    shared_appliance_kwh: float = Field(
        ...,
        ge=0.0,
        description="The total energy consumed by shared appliances in kilowatt-hours. Must be non-negative."
    )


class TransitTrackingRequest(BaseModel):
    """
    Validates daily campus travel and commuting data.
    """
    user_id: str = Field(
        ...,
        description="Anonymous device ID"
    )
    distance_km: float = Field(
        ...,
        ge=0.0,
        le=500.0,
        description="The distance traveled in kilometers. Must be between 0.0 and 500.0."
    )
    transport_mode: Literal["shared_rickshaw", "campus_shuttle", "two_wheeler", "walking"] = Field(
        ...,
        description="The mode of transport used. Restricted to recognized campus mobility options."
    )
    passenger_count: int = Field(
        ...,
        ge=1,
        description="The number of passengers sharing the transport. Must be at least 1."
    )


class WasteTrackingRequest(BaseModel):
    """
    Validates meal or cafeteria food waste data.
    """
    user_id: str = Field(
        ...,
        description="Anonymous device ID"
    )
    meal_type: Literal["breakfast", "lunch", "dinner"] = Field(
        ...,
        description="The specific meal type associated with the food waste."
    )
    estimated_waste_grams: float = Field(
        ...,
        ge=0.0,
        le=5000.0,
        description="The estimated weight of the commensal food waste in grams. Must be between 0.0 and 5000.0."
    )

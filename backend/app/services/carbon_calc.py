"""
Pure deterministic CO₂e calculation engine.

All emission factors are imported from ``factors.py`` where each constant
is named and cited from published government / intergovernmental datasets.
The functions in this module are pure — no side effects, no I/O.
"""

from app.services.factors import (
    AC_POWER_DRAW_KW,
    FOOD_WASTE_FACTOR_KG_PER_GRAM,
    GRID_EMISSION_FACTOR_KG_PER_KWH,
    TRANSIT_FACTORS,
)


def calculate_energy_co2(ac_hours: float, roommates: int, shared_kwh: float = 0.0) -> float:
    """
    Calculate per-capita CO₂e for shared residential energy usage.

    Formula::

        per_capita = ((ac_hours × AC_POWER_DRAW_KW × GRID_EF) / roommates)
                   + ((shared_kwh × GRID_EF) / roommates)

    Args:
        ac_hours: Hours of AC usage (0–24).
        roommates: Number of roommates sharing the space (≥1).
        shared_kwh: Shared appliance energy consumption in kWh (≥0).

    Returns:
        CO₂e in kg, rounded to 3 decimal places.
    """
    ac_co2 = (ac_hours * AC_POWER_DRAW_KW * GRID_EMISSION_FACTOR_KG_PER_KWH) / roommates
    appliance_co2 = (shared_kwh * GRID_EMISSION_FACTOR_KG_PER_KWH) / roommates
    return round(ac_co2 + appliance_co2, 3)


def calculate_transit_co2(distance: float, mode: str, passengers: int) -> float:
    """
    Calculate per-capita CO₂e for a transit trip, split across passengers.

    Formula::

        per_capita = (distance × mode_factor) / passengers

    Args:
        distance: Distance traveled in kilometres (≥0).
        mode: Transport mode key (rickshaw | shuttle | two_wheeler | walking).
        passengers: Number of passengers sharing the ride (≥1).

    Returns:
        CO₂e in kg, rounded to 3 decimal places.
    """
    factor = TRANSIT_FACTORS.get(mode, 0.0)  # Walking / unknown → 0.0
    return round((distance * factor) / passengers, 3)


def calculate_waste_co2(grams: float) -> float:
    """
    Calculate CO₂e for food waste.

    Formula::

        co2 = grams × FOOD_WASTE_FACTOR

    Args:
        grams: Weight of the waste in grams (≥0).

    Returns:
        CO₂e in kg, rounded to 3 decimal places.
    """
    return round(grams * FOOD_WASTE_FACTOR_KG_PER_GRAM, 3)

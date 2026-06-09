"""
Pure deterministic CO₂e calculation engine.

All emission factors are cited from published government and
intergovernmental datasets. Every constant is named and sourced
inline so the codebase contains zero unexplained magic numbers.
"""

# ── Emission Factor Sources ─────────────────────────────────────────
# Grid emission factor: India Central Electricity Authority (CEA)
# CO₂ Baseline Database v18, 2023 — weighted average for Indian grid.
GRID_EMISSION_FACTOR_KG_PER_KWH: float = 0.82

# AC power draw: Bureau of Energy Efficiency (BEE) India — typical
# 1.5-ton split AC rated at ~1.5 kW electrical input.
AC_POWER_DRAW_KW: float = 1.5

# Transit emission factors (kg CO₂e per passenger-km):
# Source: IPCC AR6 WGIII Chapter 10, Table 10.5 (2022) adapted for
# Indian urban transit modes.
TRANSIT_FACTORS: dict[str, float] = {
    "rickshaw": 0.05,       # Shared auto-rickshaw (CNG/petrol, 3-seat avg)
    "shuttle": 0.02,        # Diesel campus shuttle / public bus (high occupancy)
    "two_wheeler": 0.10,    # Petrol two-wheeler (solo rider baseline)
}

# Food waste emission factor: US EPA WARM Model v16, 2023 —
# composite factor for mixed food waste landfilled.
FOOD_WASTE_FACTOR_KG_PER_GRAM: float = 0.002


# ── Calculation Functions ───────────────────────────────────────────

def calculate_energy_co2(ac_hours: float, roommates: int, shared_kwh: float = 0.0) -> float:
    """
    Calculates the per-capita Carbon Dioxide Equivalent (CO₂e) for
    shared residential energy usage.

    Formula:
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
    Calculates the per-capita Carbon Dioxide Equivalent (CO₂e) for a
    transit trip, split across passengers.

    Formula:
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
    Calculates the Carbon Dioxide Equivalent (CO₂e) for food waste.

    Formula:
        co2 = grams × FOOD_WASTE_FACTOR

    Args:
        grams: Weight of the waste in grams (≥0).

    Returns:
        CO₂e in kg, rounded to 3 decimal places.
    """
    return round(grams * FOOD_WASTE_FACTOR_KG_PER_GRAM, 3)

"""
Published emission factors used by the carbon calculation engine.

Every constant is named and sourced from a government or intergovernmental
dataset — the codebase contains zero unexplained magic numbers.
"""

# ── Electricity Grid ────────────────────────────────────────────────
# Source: India Central Electricity Authority (CEA) CO₂ Baseline
# Database v18, 2023 — weighted average for the Indian grid.
GRID_EMISSION_FACTOR_KG_PER_KWH: float = 0.82

# ── Air Conditioning ───────────────────────────────────────────────
# Source: Bureau of Energy Efficiency (BEE) India — typical 1.5-ton
# split AC rated at ~1.5 kW electrical input.
AC_POWER_DRAW_KW: float = 1.5

# ── Transit (kg CO₂e per passenger-km) ─────────────────────────────
# Source: IPCC AR6 WGIII Chapter 10, Table 10.5 (2022) adapted for
# Indian urban transit modes.
TRANSIT_FACTORS: dict[str, float] = {
    "rickshaw": 0.05,       # Shared auto-rickshaw (CNG/petrol, 3-seat avg)
    "shuttle": 0.02,        # Diesel campus shuttle / public bus (high occupancy)
    "two_wheeler": 0.10,    # Petrol two-wheeler (solo rider baseline)
}

# ── Food Waste ──────────────────────────────────────────────────────
# Source: US EPA WARM Model v16, 2023 — composite factor for mixed
# food waste sent to landfill.
FOOD_WASTE_FACTOR_KG_PER_GRAM: float = 0.002

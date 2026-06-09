"""
Unit tests for the emission factors module.
Validates that published constants are present and within sane ranges.
"""

from app.services.factors import (
    AC_POWER_DRAW_KW,
    FOOD_WASTE_FACTOR_KG_PER_GRAM,
    GRID_EMISSION_FACTOR_KG_PER_KWH,
    TRANSIT_FACTORS,
)


class TestEmissionFactors:
    """Smoke tests that emission constants are loaded and sane."""

    def test_grid_factor_is_positive(self) -> None:
        assert GRID_EMISSION_FACTOR_KG_PER_KWH > 0

    def test_grid_factor_within_range(self) -> None:
        # Global grid factors range from ~0.1 (Norway hydro) to ~1.2 (coal-heavy)
        assert 0.1 <= GRID_EMISSION_FACTOR_KG_PER_KWH <= 1.5

    def test_ac_power_draw_is_positive(self) -> None:
        assert AC_POWER_DRAW_KW > 0

    def test_transit_factors_has_expected_modes(self) -> None:
        expected_modes = {"rickshaw", "shuttle", "two_wheeler"}
        assert expected_modes.issubset(set(TRANSIT_FACTORS.keys()))

    def test_transit_factors_are_positive(self) -> None:
        for mode, factor in TRANSIT_FACTORS.items():
            assert factor > 0, f"{mode} factor should be positive"

    def test_walking_not_in_transit_factors(self) -> None:
        # Walking should return 0.0 via .get() default, not be in the dict
        assert "walking" not in TRANSIT_FACTORS

    def test_food_waste_factor_is_positive(self) -> None:
        assert FOOD_WASTE_FACTOR_KG_PER_GRAM > 0

    def test_food_waste_factor_is_small(self) -> None:
        # Factor should be small (grams to kg conversion)
        assert FOOD_WASTE_FACTOR_KG_PER_GRAM < 0.1

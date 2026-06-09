"""
Unit tests for the pure deterministic CO2e calculation functions.
Tests cover normal inputs, edge cases, zero values, and boundary conditions.
"""
import pytest

from app.services.carbon_calc import (
    calculate_energy_co2,
    calculate_transit_co2,
    calculate_waste_co2,
)


# ── Energy CO2 Calculation ──────────────────────────────────────────

class TestCalculateEnergyCo2:
    """Tests for calculate_energy_co2."""

    def test_basic_calculation(self) -> None:
        """Standard scenario: 5 AC hours, 2 roommates, 100 kWh shared."""
        result = calculate_energy_co2(ac_hours=5, roommates=2, shared_kwh=100)
        expected = round(((5 * 1.5 * 0.82) / 2) + ((100 * 0.82) / 2), 3)
        assert result == expected

    def test_single_roommate(self) -> None:
        """Solo occupant bears the full energy burden."""
        result = calculate_energy_co2(ac_hours=8, roommates=1, shared_kwh=50)
        expected = round((8 * 1.5 * 0.82) + (50 * 0.82), 3)
        assert result == expected

    def test_zero_ac_hours(self) -> None:
        """No AC usage should only account for shared appliance energy."""
        result = calculate_energy_co2(ac_hours=0, roommates=3, shared_kwh=60)
        expected = round((60 * 0.82) / 3, 3)
        assert result == expected

    def test_zero_shared_kwh(self) -> None:
        """No shared appliance usage should only account for AC."""
        result = calculate_energy_co2(ac_hours=10, roommates=4)
        expected = round((10 * 1.5 * 0.82) / 4, 3)
        assert result == expected

    def test_zero_everything(self) -> None:
        """All zeros should return 0.0."""
        result = calculate_energy_co2(ac_hours=0, roommates=1, shared_kwh=0)
        assert result == 0.0

    def test_large_roommate_count(self) -> None:
        """Many roommates drastically reduce per-capita emissions."""
        result = calculate_energy_co2(ac_hours=24, roommates=10, shared_kwh=500)
        assert result > 0
        assert result < calculate_energy_co2(ac_hours=24, roommates=1, shared_kwh=500)

    def test_return_type_is_float(self) -> None:
        """Return type must always be float."""
        result = calculate_energy_co2(ac_hours=3, roommates=2, shared_kwh=10)
        assert isinstance(result, float)

    def test_precision_three_decimals(self) -> None:
        """Result should be rounded to exactly 3 decimal places."""
        result = calculate_energy_co2(ac_hours=7, roommates=3, shared_kwh=33)
        assert result == round(result, 3)


# ── Transit CO2 Calculation ─────────────────────────────────────────

class TestCalculateTransitCo2:
    """Tests for calculate_transit_co2."""

    def test_rickshaw_mode(self) -> None:
        """Rickshaw at 10 km, 2 passengers."""
        result = calculate_transit_co2(distance=10, mode="rickshaw", passengers=2)
        expected = round((10 * 0.05) / 2, 3)
        assert result == expected

    def test_shuttle_mode(self) -> None:
        """Campus shuttle at 20 km, 1 passenger."""
        result = calculate_transit_co2(distance=20, mode="shuttle", passengers=1)
        expected = round(20 * 0.02, 3)
        assert result == expected

    def test_two_wheeler_mode(self) -> None:
        """Two-wheeler at 15 km, 1 passenger."""
        result = calculate_transit_co2(distance=15, mode="two_wheeler", passengers=1)
        expected = round(15 * 0.10, 3)
        assert result == expected

    def test_walking_returns_zero(self) -> None:
        """Walking should produce zero emissions."""
        result = calculate_transit_co2(distance=5, mode="walking", passengers=1)
        assert result == 0.0

    def test_unknown_mode_returns_zero(self) -> None:
        """An unrecognized mode should safely default to zero."""
        result = calculate_transit_co2(distance=100, mode="teleportation", passengers=1)
        assert result == 0.0

    def test_zero_distance(self) -> None:
        """Zero distance traveled always means zero emissions."""
        result = calculate_transit_co2(distance=0, mode="rickshaw", passengers=1)
        assert result == 0.0

    def test_more_passengers_reduce_co2(self) -> None:
        """Carpooling with more passengers must reduce per-capita CO2."""
        solo = calculate_transit_co2(distance=30, mode="rickshaw", passengers=1)
        shared = calculate_transit_co2(distance=30, mode="rickshaw", passengers=3)
        assert shared < solo

    def test_return_type_is_float(self) -> None:
        """Return type must always be float."""
        result = calculate_transit_co2(distance=10, mode="shuttle", passengers=2)
        assert isinstance(result, float)


# ── Waste CO2 Calculation ───────────────────────────────────────────

class TestCalculateWasteCo2:
    """Tests for calculate_waste_co2."""

    def test_basic_calculation(self) -> None:
        """250g of waste at the standard factor."""
        result = calculate_waste_co2(grams=250)
        assert result == 0.5

    def test_zero_waste(self) -> None:
        """No waste means zero emissions."""
        result = calculate_waste_co2(grams=0)
        assert result == 0.0

    def test_large_waste(self) -> None:
        """5 kg of waste (upper boundary)."""
        result = calculate_waste_co2(grams=5000)
        assert result == 10.0

    def test_small_waste(self) -> None:
        """Very small portions."""
        result = calculate_waste_co2(grams=1)
        assert result == 0.002

    def test_return_type_is_float(self) -> None:
        """Return type must always be float."""
        result = calculate_waste_co2(grams=100)
        assert isinstance(result, float)

    def test_precision_three_decimals(self) -> None:
        """Result should be rounded to exactly 3 decimal places."""
        result = calculate_waste_co2(grams=333)
        assert result == round(result, 3)

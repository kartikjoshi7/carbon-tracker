"""
Integration tests for the Carbon Engine FastAPI endpoints.
Uses FastAPI's TestClient to validate HTTP status codes,
response structure, and Pydantic validation error handling.
"""
from fastapi.testclient import TestClient

# ── Health Check ────────────────────────────────────────────────────

class TestHealthCheck:
    """Tests for the root health-check endpoint."""

    def test_health_check_returns_200(self, client: TestClient) -> None:
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_check_response_body(self, client: TestClient) -> None:
        data = client.get("/api/health").json()
        assert data["status"] == "online"
        assert "message" in data


# ── Energy Endpoint ─────────────────────────────────────────────────

class TestEnergyEndpoint:
    """Tests for POST /api/v1/footprint/energy."""

    def test_valid_energy_request(self, client: TestClient) -> None:
        payload = {
            "user_id": "test_user",
            "roommate_count": 3,
            "ac_hours_logged": 5.5,
            "shared_appliance_kwh": 120.5,
        }
        response = client.post("/api/v1/footprint/energy", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "calculated_co2" in data
        assert isinstance(data["calculated_co2"], float)

    def test_energy_missing_field_returns_422(self, client: TestClient) -> None:
        """Missing required fields should trigger Pydantic validation."""
        payload = {"roommate_count": 2}
        response = client.post("/api/v1/footprint/energy", json=payload)
        assert response.status_code == 422

    def test_energy_invalid_ac_hours_returns_422(self, client: TestClient) -> None:
        """AC hours exceeding 24 should fail validation."""
        payload = {
            "user_id": "test_user",
            "roommate_count": 1,
            "ac_hours_logged": 25.0,
            "shared_appliance_kwh": 10,
        }
        response = client.post("/api/v1/footprint/energy", json=payload)
        assert response.status_code == 422

    def test_energy_zero_roommates_returns_422(self, client: TestClient) -> None:
        """Zero roommates is invalid (ge=1)."""
        payload = {
            "user_id": "test_user",
            "roommate_count": 0,
            "ac_hours_logged": 5,
            "shared_appliance_kwh": 10,
        }
        response = client.post("/api/v1/footprint/energy", json=payload)
        assert response.status_code == 422


# ── Transit Endpoint ────────────────────────────────────────────────

class TestTransitEndpoint:
    """Tests for POST /api/v1/footprint/transit."""

    def test_valid_transit_request(self, client: TestClient) -> None:
        payload = {
            "user_id": "test_user",
            "distance_km": 12.5,
            "transport_mode": "shared_rickshaw",
            "passenger_count": 3,
        }
        response = client.post("/api/v1/footprint/transit", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "calculated_co2" in data
        assert isinstance(data["calculated_co2"], float)

    def test_transit_invalid_mode_returns_422(self, client: TestClient) -> None:
        """An unrecognized transport mode should fail Literal validation."""
        payload = {
            "user_id": "test_user",
            "distance_km": 10,
            "transport_mode": "helicopter",
            "passenger_count": 1,
        }
        response = client.post("/api/v1/footprint/transit", json=payload)
        assert response.status_code == 422

    def test_transit_walking_returns_zero_co2(self, client: TestClient) -> None:
        """Walking mode should calculate zero emissions."""
        payload = {
            "user_id": "test_user",
            "distance_km": 5,
            "transport_mode": "walking",
            "passenger_count": 1,
        }
        response = client.post("/api/v1/footprint/transit", json=payload)
        assert response.status_code == 200
        assert response.json()["calculated_co2"] == 0.0

    def test_transit_negative_distance_returns_422(self, client: TestClient) -> None:
        """Negative distance is invalid (ge=0)."""
        payload = {
            "user_id": "test_user",
            "distance_km": -5,
            "transport_mode": "campus_shuttle",
            "passenger_count": 1,
        }
        response = client.post("/api/v1/footprint/transit", json=payload)
        assert response.status_code == 422


# ── Waste Endpoint ──────────────────────────────────────────────────

class TestWasteEndpoint:
    """Tests for POST /api/v1/footprint/waste."""

    def test_valid_waste_request(self, client: TestClient) -> None:
        payload = {
            "user_id": "test_user",
            "meal_type": "lunch",
            "estimated_waste_grams": 250,
        }
        response = client.post("/api/v1/footprint/waste", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["calculated_co2"] == 0.5

    def test_waste_invalid_meal_type_returns_422(self, client: TestClient) -> None:
        """An unrecognized meal type should fail Literal validation."""
        payload = {
            "user_id": "test_user",
            "meal_type": "midnight_snack",
            "estimated_waste_grams": 100,
        }
        response = client.post("/api/v1/footprint/waste", json=payload)
        assert response.status_code == 422

    def test_waste_exceeds_max_returns_422(self, client: TestClient) -> None:
        """Waste exceeding 5000g should fail validation."""
        payload = {
            "user_id": "test_user",
            "meal_type": "dinner",
            "estimated_waste_grams": 6000,
        }
        response = client.post("/api/v1/footprint/waste", json=payload)
        assert response.status_code == 422


# ── History & Leaderboard Endpoints ─────────────────────────────────

class TestHistoryAndLeaderboard:
    """Tests for the data retrieval endpoints."""

    def test_history_returns_200(self, client: TestClient) -> None:
        response = client.get("/api/v1/footprint/history/user_123")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert isinstance(data["history"], list)

    def test_leaderboard_returns_200(self, client: TestClient) -> None:
        response = client.get("/api/v1/footprint/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert "leaderboard" in data
        assert isinstance(data["leaderboard"], list)

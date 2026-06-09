"""
Unit tests for the database service module.
Tests Supabase persistence layer, mock fallback, and error handling.
"""


# ── Insert Footprint Log ───────────────────────────────────────────

class TestInsertFootprintLog:
    """Tests for the insert_footprint_log function."""

    def test_no_db_returns_none(self) -> None:
        from app.services.database import insert_footprint_log
        result = insert_footprint_log(db=None, user_id="test", category="energy", metric_value=5.0, calculated_co2=6.15)
        assert result is None

    def test_db_exception_returns_none(self) -> None:
        from app.services.database import insert_footprint_log

        class FakeDB:
            def table(self, name: str):
                raise RuntimeError("DB connection failed")

        result = insert_footprint_log(db=FakeDB(), user_id="test", category="energy", metric_value=5.0, calculated_co2=6.15)
        assert result is None


# ── Get Footprint History ──────────────────────────────────────────

class TestGetFootprintHistory:
    """Tests for the get_footprint_history function."""

    def test_no_db_returns_mock_data(self) -> None:
        from app.services.database import get_footprint_history
        result = get_footprint_history(db=None, user_id="test")
        assert isinstance(result, list)
        assert len(result) > 0
        assert "category" in result[0]

    def test_db_exception_returns_mock_data(self) -> None:
        from app.services.database import get_footprint_history

        class FakeDB:
            def table(self, name: str):
                raise RuntimeError("DB connection failed")

        result = get_footprint_history(db=FakeDB(), user_id="test")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_mock_data_has_required_fields(self) -> None:
        from app.services.database import get_footprint_history
        result = get_footprint_history(db=None, user_id="test")
        for entry in result:
            assert "category" in entry
            assert "calculated_co2" in entry
            assert "created_at" in entry


# ── Get Leaderboard ────────────────────────────────────────────────

class TestGetLeaderboard:
    """Tests for the get_leaderboard function."""

    def test_no_db_returns_mock_leaderboard(self) -> None:
        from app.services.database import get_leaderboard
        result = get_leaderboard(db=None)
        assert isinstance(result, list)
        assert len(result) > 0
        assert "user_id" in result[0]
        assert "total_co2" in result[0]

    def test_db_exception_returns_mock_leaderboard(self) -> None:
        from app.services.database import get_leaderboard

        class FakeDB:
            def table(self, name: str):
                raise RuntimeError("DB connection failed")

        result = get_leaderboard(db=FakeDB())
        assert isinstance(result, list)
        assert len(result) > 0

    def test_mock_leaderboard_is_sorted(self) -> None:
        from app.services.database import get_leaderboard
        result = get_leaderboard(db=None)
        co2_values = [entry["total_co2"] for entry in result]
        assert co2_values == sorted(co2_values)

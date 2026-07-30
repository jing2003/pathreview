"""Tests for api/routes/health.py."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from api.routes.health import health_check
from core.config import settings


@pytest.mark.unit
class TestHealthCheck:
    """Test suite for the health-check endpoint."""

    @pytest.mark.asyncio
    async def test_reports_total_safety_event_count(self) -> None:
        """Test the health response includes the monitoring total."""
        mock_db = AsyncMock()
        mock_redis = Mock()
        mock_monitor = Mock()
        mock_monitor.get_total_event_count.return_value = 7

        with (
            patch(
                "api.routes.health.redis.Redis.from_url",
                return_value=mock_redis,
            ) as mock_from_url,
            patch(
                "api.routes.health.SafetyMonitor",
                return_value=mock_monitor,
            ) as mock_monitor_class,
        ):
            result = await health_check(mock_db)

        assert result["safety_events_last_hour"] == 7
        assert result["dependencies"]["postgres"] == "healthy"
        assert result["dependencies"]["redis"] == "healthy"

        mock_db.execute.assert_awaited_once_with("SELECT 1")
        mock_redis.ping.assert_called_once_with()
        mock_from_url.assert_called_once_with(
            settings.redis_url,
            decode_responses=True,
        )
        mock_monitor_class.assert_called_once_with(mock_redis)
        mock_monitor.get_total_event_count.assert_called_once_with(
            window_hours=1,
        )

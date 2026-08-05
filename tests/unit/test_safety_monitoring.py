"""Tests for safety/monitoring.py."""

from typing import TYPE_CHECKING, cast
from unittest.mock import Mock

import pytest

from safety.monitoring import SafetyMonitor

if TYPE_CHECKING:
    import redis


@pytest.mark.unit
class TestSafetyMonitor:
    """Test suite for SafetyMonitor."""

    @pytest.fixture
    def mock_redis(self) -> Mock:
        """Create a mocked Redis client."""
        return Mock()

    @pytest.fixture
    def monitor(self, mock_redis: Mock) -> SafetyMonitor:
        """Create a SafetyMonitor with mocked Redis."""
        return SafetyMonitor(cast("redis.Redis", mock_redis))

    def test_total_event_count_sums_valid_event_types(
        self,
        monitor: SafetyMonitor,
        mock_redis: Mock,
    ) -> None:
        """Test counts across valid event types are summed."""

        counts = {
            "safety:events:pii_detected": "2",
            "safety:events:bias_detected": "3",
        }

        def get_count(key: str) -> str | None:
            return counts.get(key)

        mock_redis.get.side_effect = get_count

        total = monitor.get_total_event_count()

        assert total == 5
        assert mock_redis.get.call_count == len(SafetyMonitor.VALID_EVENT_TYPES)

    def test_total_event_count_returns_zero_when_no_events(
        self,
        monitor: SafetyMonitor,
        mock_redis: Mock,
    ) -> None:
        """Test zero is returned when no event counters exist."""
        mock_redis.get.return_value = None

        total = monitor.get_total_event_count()

        assert total == 0

    def test_total_event_count_handles_redis_errors(
        self,
        monitor: SafetyMonitor,
        mock_redis: Mock,
    ) -> None:
        """Test Redis errors result in a safe zero count."""
        mock_redis.get.side_effect = Exception("Redis unavailable")

        total = monitor.get_total_event_count()

        assert total == 0

import pytest
from meal_planner.lib import UnitSystem


def test_from_str():
    assert UnitSystem.from_str("metric") is UnitSystem.METRIC
    assert UnitSystem.from_str("imperial") is UnitSystem.IMPERIAL


def test_invalid_from_str():
    with pytest.raises(ValueError):
        UnitSystem.from_str("natural")


def test_values():
    assert UnitSystem.METRIC.value == "metric"
    assert UnitSystem.IMPERIAL.value == "imperial"

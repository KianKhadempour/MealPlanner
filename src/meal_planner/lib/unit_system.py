from __future__ import annotations

from enum import Enum


class UnitSystem(Enum):
    METRIC = "metric"
    IMPERIAL = "imperial"

    @classmethod
    def from_str(cls, input_str: str) -> UnitSystem:
        match input_str:
            case "metric":
                return cls.METRIC
            case "imperial":
                return cls.IMPERIAL
            case _:
                raise ValueError("Only metric and imperial are supported")

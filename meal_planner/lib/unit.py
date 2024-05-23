from dataclasses import dataclass

from unit_system import UnitSystem


@dataclass(frozen=True, slots=True)
class Unit:
    name: str
    display_plural: str
    display_singular: str
    abbreviation: str
    system: UnitSystem
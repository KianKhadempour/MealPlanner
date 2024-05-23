from dataclasses import dataclass

from ingredient import Ingredient
from unit import Unit


@dataclass(frozen=True, slots=True)
class Component:
    ingredient: Ingredient
    unit: Unit | None
    quantity: float

from dataclasses import dataclass

from meal_planner.lib.ingredient import Ingredient
from meal_planner.lib.unit import Unit


@dataclass(frozen=True, slots=True)
class Component:
    ingredient: Ingredient
    unit: Unit | None
    quantity: float

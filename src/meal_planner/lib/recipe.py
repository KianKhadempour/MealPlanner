from dataclasses import dataclass

from meal_planner.lib.component import Component


@dataclass(frozen=True, slots=True)
class Recipe:
    name: str
    id: int
    servings: int
    components: list[Component]

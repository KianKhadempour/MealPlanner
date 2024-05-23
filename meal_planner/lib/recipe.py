from dataclasses import dataclass

from component import Component


@dataclass(frozen=True, slots=True)
class Recipe:
    name: str
    id: int
    servings: int
    components: list[Component]

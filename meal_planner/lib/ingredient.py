from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Ingredient:
    id: int
    display_plural: str
    display_singular: str

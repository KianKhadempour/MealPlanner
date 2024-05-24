from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Tag:
    id: int
    type: str
    name: str
    display_name: str

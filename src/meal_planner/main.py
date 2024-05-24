from collections.abc import Collection

from meal_planner.lib import Component, Recipe, Tag


def get_matching_recipes(
    all_recipes: Collection[Recipe], n_recipes: int
) -> list[Recipe]:
    raise NotImplementedError()


def get_components(recipes: Collection[Recipe]) -> list[Component]:
    raise NotImplementedError()


def make_shopping_list(components: Collection[Component]) -> str:
    raise NotImplementedError()


def get_n_recipes() -> int:
    raise NotImplementedError()


def get_preferred_recipes() -> list[Recipe]:
    raise NotImplementedError()


def get_preferred_tags(preferred_recipes: Collection[Recipe]) -> list[Tag]:
    raise NotImplementedError()

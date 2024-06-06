from __future__ import annotations

import itertools
import json
import threading
import time
from collections.abc import Callable, Iterable
from contextlib import AbstractContextManager
from enum import Enum
from pathlib import Path
from typing import Any

from tasty_api import SortingMethod
from tasty_api.data import CompletionData, RecipeListData
from tasty_api.recipe import Completion, Component, Recipe
from tasty_api.tag import Tag


def get_matching_recipes(
    recipes: Iterable[Recipe], n_recipes: int, tag_points: dict[int, int]
) -> list[Recipe]:
    scores: list[tuple[Recipe, int]] = []

    for recipe in recipes:
        recipe_score = 0
        for tag in recipes:
            if tag_score := tag_points.get(tag.metadata.id):
                recipe_score += tag_score

        scores.append((recipe, recipe_score))

    return [score[0] for score in sorted(scores, key=lambda s: s[1], reverse=True)][
        :n_recipes
    ]


def get_components(recipes: Iterable[Recipe]) -> list[Component]:
    components: list[Component] = []
    for recipe in recipes:
        for section in recipe.sections:
            for component in section.components:
                components.append(component)

    return components


def make_shopping_list(components: Iterable[Component]) -> str:
    shopping_list: list[Component] = []
    for component in components:
        if component.ingredient.id in [
            component_.ingredient.id for component_ in shopping_list
        ]:
            for i, component__ in enumerate(shopping_list):
                if component.ingredient.id != component__.ingredient.id:
                    continue
                shopping_list[i] = component + component__
        else:
            shopping_list.append(component)

    list_items: list[str] = []
    for component in shopping_list:
        if component.measurements[0].quantity == 0:
            list_items.append(component.ingredient.display_singular)
        else:
            list_items.append(
                "".join(
                    (
                        component.ingredient.display_singular,
                        ": ",
                        str(
                            int(component.measurements[0].quantity)
                            if component.measurements[0].quantity.is_integer()
                            else round(component.measurements[0].quantity, 2)
                        ),
                        " ",
                        component.measurements[0].unit.abbreviation,
                    )
                )
            )

    return "\n".join(list_items)


def validation_input[T](
    type_: Callable[[str], T], prompt: str = "", message_on_fail: str | None = None
) -> T:
    while True:
        n = input(prompt)
        try:
            return type_(n)
        except (ValueError, TypeError):
            if message_on_fail is None:
                extra_n = (
                    "n" if type_.__name__.startswith(("a", "e", "i", "o", "u")) else ""
                )
                print(
                    f"Your input could not be converted to a{extra_n} {type_.__name__}."
                )
            else:
                print(message_on_fail)


def get_preferred_recipes() -> list[Recipe]:
    raise NotImplementedError()


def get_preferred_tags(preferred_recipes: Iterable[Recipe]) -> list[Tag]:
    preferred_tags: list[Tag] = []
    for recipe in preferred_recipes:
        preferred_tags.extend(recipe.tags)

    return preferred_tags


class Loader(AbstractContextManager[None]):
    def __init__(self, text: str) -> None:
        self.text = text
        self.done = threading.Event()
        self.thread = threading.Thread(target=self.load)

    def load(self):
        for c in itertools.cycle(["|", "/", "-", "\\"]):
            if self.done.is_set():
                break
            print(f"\r{self.text} {c}", end="", flush=True)
            time.sleep(0.1)
        print(f"\rDone!{"".join(" " for _ in self.text)}", flush=True)

    def __enter__(self) -> None:
        self.thread.start()

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        self.done.set()
        self.thread.join()


class Rating(Enum):
    DISLIKE = -1
    NONE = 0
    LIKE = 1
    LOVE = 2

    @classmethod
    def from_str(cls, input_: str) -> Rating:
        match input_.lower():
            case "dislike":
                return Rating.DISLIKE
            case "none":
                return Rating.NONE
            case "like":
                return Rating.LIKE
            case "love":
                return Rating.LOVE
            case _:
                raise ValueError(
                    "from_str must be called with either dislike, none, like, or love."
                )


class FakeClient:
    def __init__(self):
        self.data_folder = Path().cwd().joinpath("data")

    def get_recipes_auto_complete(self, prefix: str) -> list[Completion]:
        """
        Get auto complete suggestions by name or ingredients.

        :param str prefix: The text to be auto completed.
        :return list[Completion]: A list of possible auto completions.
        """

        with open(
            self.data_folder.joinpath("recipes-auto-complete.json"), encoding="UTF-8"
        ) as f:
            data = CompletionData.from_dict(json.load(f))

        return data.results

    def get_recipes_list(
        self,
        offset: int,
        size: int,
        tags: list[Tag] | None = None,
        query: str | None = None,
        sort: SortingMethod = SortingMethod.POPULAR,
    ) -> list[Recipe]:
        """
        Get a list of recipes.

        :param int offset: The amount of recipes to skip.
        :param int size: The amount of recipes to get.
        :param list[Tag] | None tags: A list of tags you want to search for, defaults to None
        :param str | None query: Name of food or ingredients to search by, defaults to None
        :param SortingMethod sort: The method of sorting the results, defaults to SortingMethod.POPULAR
        :return list[Recipe]: The list of recipes.
        """
        time.sleep(3)
        with open(
            self.data_folder.joinpath("recipes-list.json"), encoding="UTF-8"
        ) as f:
            data = RecipeListData.from_dict(json.load(f))

        return data.results

import datetime
import itertools
import json
import os
import threading
import time
from collections.abc import Collection
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Callable

import sqlalchemy as sa
from tasty_api import SortingMethod
from tasty_api.data import CompletionData, RecipeListData
from tasty_api.recipe import Completion, Component, Recipe
from tasty_api.tag import Tag

from meal_planner.lib.sql import (
    Mode,
    get_mode,
    get_offset,
    get_tag_points,
    increment_offset,
)


def get_matching_recipes(
    recipes: Collection[Recipe], n_recipes: int, tag_points: dict[int, int]
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


def get_components(recipes: Collection[Recipe]) -> list[Component]:
    components: list[Component] = []
    for recipe in recipes:
        for section in recipe.sections:
            for component in section.components:
                components.append(component)

    return components


def make_shopping_list(components: Collection[Component]) -> str:
    shopping_list: list[Component] = []
    for component in components:
        if component.id in [component_.id for component_ in shopping_list]:
            for i, component__ in enumerate(shopping_list):
                if component.id != component__.id:
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


def get_preferred_tags(preferred_recipes: Collection[Recipe]) -> list[Tag]:
    preferred_tags: list[Tag] = []
    for recipe in preferred_recipes:
        preferred_tags.extend(recipe.tags)

    return preferred_tags


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

    # def get_recipes_list_similarities(self, recipe_id: int) -> list[Recipe]:
    #     """
    #     Get a list of recipes similar to a given recipe.

    #     :param int recipe_id: The recipe to get similar recipes to.
    #     :return list[Recipe]: The list of similar recipes.
    #     """

    #     url = "https://tasty.p.rapidapi.com/recipes/list-similarities"

    #     querystring = {"recipe_id": str(recipe_id)}

    #     response = self._session.get(url, params=querystring)

    #     data = RecipeListData.from_dict(response.json())

    #     return data.results

    # def get_recipes_more_info(self, recipe_id: int) -> Recipe:
    #     """
    #     Get a specific recipe.

    #     :param int recipe_id: The recipe to get information on.
    #     :return Recipe: The recipe.
    #     """

    #     url = "https://tasty.p.rapidapi.com/recipes/get-more-info"

    #     querystring = {"recipe_id": recipe_id}

    #     response = self._session.get(url, params=querystring)

    #     recipe = Recipe.from_dict(response.json())

    #     return recipe

    # def get_feeds_list(
    #     self,
    #     vegetarian: bool,
    #     timezone: tzinfo = UTC,
    #     offset: int = 0,
    #     size: int = 5,
    # ) -> list[Feed]:
    #     """
    #     Get a list of the latests feeds.

    #     Feeds are lists of specifically categorized recipes.

    #     :param int offset: The amount of feeds to skip.
    #     :param int size: The amount of feeds to get.
    #     :param bool vegetarian: List vegetarian recipes only.
    #     :param tzinfo timezone: Your timezone. Defaults to UTC.
    #     :return list[Feed]: The list of feeds.
    #     """

    #     url = "https://tasty.p.rapidapi.com/feeds/list"

    #     querystring = {
    #         "size": str(size),
    #         "timezone": _timezone_to_utc_offset(timezone),
    #         "vegetarian": "true" if vegetarian else "false",
    #         "from": str(offset),
    #     }

    #     response = self._session.get(url, params=querystring)

    #     data = [Feed.from_dict(result) for result in response.json()["results"]]

    #     return data

    # def get_tags_list(self) -> list[Tag]:
    #     """
    #     Get a list of all tags.

    #     :return list[Tag]: The list of tags.
    #     """

    #     url = "https://tasty.p.rapidapi.com/tags/list"

    #     response = self._session.get(url)

    #     data = TagListData.from_dict(response.json())

    #     return data.results

    # def get_tips_list(
    #     self, recipe_id: int, offset: int = 0, size: int = 30
    # ) -> list[Tip]:
    #     """
    #     Get a list of tips (reviews) pertaining to a recipe.

    #     :param int recipe_id: The recipe ID.
    #     :param int offset: The amount of tips to skip.
    #     :param int size: The amount of tips to get.

    #     :return list[Tip]: The list of tips.
    #     """

    #     url = "https://tasty.p.rapidapi.com/tips/list"

    #     querystring = {
    #         "id": str(recipe_id),
    #         "from": str(offset),
    #         "size": str(size),
    #     }

    #     response = self._session.get(url, params=querystring)

    #     data = TipListData.from_dict(response.json())

    #     return data.results


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

    def __exit__(self, *args, **kwargs) -> None:
        self.done.set()
        self.thread.join()


def prepare(conn: sa.Connection) -> None:
    client = FakeClient()

    n_recipes = validation_input(int, "How many recipes do you want? ")
    with Loader("Searching recipes"):
        all_recipes = client.get_recipes_list(offset=get_offset(conn), size=200)

    recipes = get_matching_recipes(all_recipes, n_recipes, get_tag_points(conn))

    components = get_components(recipes)
    shopping_list = make_shopping_list(components)
    today = datetime.date.today().isoformat()
    now = datetime.datetime.now().strftime("%H:%M:%S")

    with open(
        f"shopping-list-{today}.txt",
        mode="a",
        encoding="UTF-8",
    ) as f:
        print(now, file=f)
        print("-" * len(now), file=f)
        print(shopping_list, file=f, end="\n\n")
    print(f"Saved shopping list to shopping-list-{today}.txt")

    with open(
        f"recipes-{today}.txt",
        mode="a",
        encoding="UTF-8",
    ) as f:
        print(now, file=f)
        print("-" * len(now), file=f)
        for recipe in recipes:
            print(f"https://tasty.co/recipe/{recipe.metadata.slug}/", file=f)
    print(f"Saved recipes to recipes-{today}.txt")

    os.startfile(f"shopping-list-{today}.txt")
    os.startfile(f"recipes-{today}.txt")

    increment_offset(n_recipes, conn)


def main() -> None:
    engine = sa.create_engine("sqlite+pysqlite:///test.db")

    with engine.connect() as conn:
        mode = get_mode(conn)

        if mode == Mode.PREPARE:
            prepare(conn)
        # else:
        #     review(conn)


if __name__ == "__main__":
    main()

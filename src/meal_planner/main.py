import datetime
import os
import sys

import sqlalchemy as sa
from dotenv import load_dotenv
from tasty_api import Client

from meal_planner.lib.helpers import (
    Loader,
    Rating,
    get_components,
    get_matching_recipes,
    make_shopping_list,
    validation_input,
)
from meal_planner.lib.sql import (
    Mode,
    delete_previous_recipes,
    get_mode,
    get_offset,
    get_previous_recipes,
    get_recipe_tags,
    get_tag_points,
    increment_offset,
    set_mode,
    store_previous_recipes,
    store_recipes,
    update_tag,
)

load_dotenv()


def prepare(conn: sa.Connection) -> None:
    key = os.environ.get("TASTY_API_KEY")
    if key is None:
        print("Please enter your Tasty api key and try again.", file=sys.stderr)
        exit(1)

    client = Client(key)

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

    store_recipes(recipes, conn)
    store_previous_recipes(recipes, conn)

    increment_offset(n_recipes, conn)
    set_mode(Mode.REVIEW, conn)


def review(conn: sa.Connection) -> None:
    for recipe_id, recipe_name in get_previous_recipes(conn):
        rating = validation_input(
            Rating.from_str,
            f"How did you like {recipe_name} (dislike, none, like, or love)? ",
            "Please enter dislike, none, like, or love",
        )

        for tag_id in get_recipe_tags(recipe_id, conn):
            update_tag(tag_id, conn, rating.value)

    delete_previous_recipes(conn)
    set_mode(Mode.PREPARE, conn)


def main() -> None:
    engine = sa.create_engine("sqlite+pysqlite:///test.db")

    with engine.begin() as conn:
        mode = get_mode(conn)

        if mode == Mode.PREPARE:
            prepare(conn)
        else:
            review(conn)


if __name__ == "__main__":
    main()

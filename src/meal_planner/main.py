import json
from collections.abc import Collection
from enum import StrEnum, auto
from pprint import pprint

import sqlalchemy as sa
from tasty_api.data import RecipeListData
from tasty_api.recipe import Component, Recipe
from tasty_api.tag import Tag


def get_matching_recipes(
    all_recipes: Collection[Recipe], n_recipes: int
) -> list[Recipe]:
    raise NotImplementedError()


def get_components(recipes: Collection[Recipe]) -> list[Component]:
    components: list[Component] = []
    for recipe in recipes:
        for section in recipe.sections:
            for component in section.components:
                components.append(component)

    return components


def make_shopping_list(components: Collection[Component]) -> str:
    raise NotImplementedError()


def validation_input(type_: type, prompt: str = "") -> int:
    while True:
        n = input(prompt)
        try:
            return type_(n)
        except ValueError:
            print(
                f"Your input could not be converted to a{"n" if type_.__name__.startswith(("a", "e", "i", "o", "u")) else ""} {type_.__name__}."
            )


def get_preferred_recipes() -> list[Recipe]:
    raise NotImplementedError()


def get_preferred_tags(preferred_recipes: Collection[Recipe]) -> list[Tag]:
    preferred_tags: list[Tag] = []
    for recipe in preferred_recipes:
        preferred_tags.extend(recipe.tags)

    return preferred_tags


def store_tag(tag: Tag, conn: sa.Connection) -> None:
    conn.execute(
        sa.text("""
        INSERT OR IGNORE INTO tags (id, likes) VALUES (:id, 0)
    """),
        {"id": tag.id},
    )


def store_tags(tags: Collection[Tag], conn: sa.Connection) -> None:
    for tag in tags:
        store_tag(tag, conn)


def update_tag(tag: Tag, conn: sa.Connection, change_in_likes: int) -> None:
    conn.execute(
        sa.text("""
        UPDATE tags
        SET likes = likes + :change_in_likes
        WHERE id = :id
    """),
        {"change_in_likes": change_in_likes, "id": tag.id},
    )


def like_tags(tags: Collection[Tag], conn: sa.Connection) -> None:
    for tag in tags:
        update_tag(tag, conn, 1)


def store_recipe(recipe: Recipe, conn: sa.Connection) -> None:
    conn.execute(
        sa.text("INSERT OR IGNORE INTO recipes (id, name) VALUES (:id, :name)"),
        {"id": recipe.metadata.id, "name": recipe.name},
    )

    store_tags(recipe.tags, conn)


def store_recipe_tag_relationship(
    recipe: Recipe, tag: Tag, conn: sa.Connection
) -> None:
    conn.execute(
        sa.text(
            "INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (:recipe_id, :tag_id)"
        ),
        {"recipe_id": recipe.metadata.id, "tag_id": tag.id},
    )


def store_recipes(recipes: Collection[Recipe], conn: sa.Connection) -> None:
    for recipe in recipes:
        store_recipe(recipe, conn)
        for tag in recipe.tags:
            store_recipe_tag_relationship(recipe, tag, conn)


class TableType(StrEnum):
    RECIPES = auto()
    TAGS = auto()
    RECIPE_TAGS = auto()


def print_table(table_type: TableType, conn: sa.Connection) -> None:
    pprint(conn.execute(sa.text(f"SELECT * FROM {table_type}")).all())


def main() -> None:
    engine = sa.create_engine("sqlite+pysqlite:///test.db")

    with open("data/recipes-list.json", encoding="UTF-8") as f:
        recipe_list_data = RecipeListData.from_dict(json.load(f))
        recipes = recipe_list_data.results

    with engine.begin() as conn:
        store_recipes(recipes, conn)


if __name__ == "__main__":
    main()

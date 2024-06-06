from __future__ import annotations

from collections.abc import Iterable
from enum import Enum, StrEnum, auto
from pprint import pprint
from typing import NamedTuple

import sqlalchemy as sa
from tasty_api.recipe import Recipe
from tasty_api.tag import Tag


class NoDataFoundError(Exception):
    """Exception raised when no data is found in the database."""

    pass


def store_tag(tag: Tag, conn: sa.Connection) -> None:
    conn.execute(
        sa.text("INSERT OR IGNORE INTO tags (id, likes) VALUES (:id, 0)"),
        {"id": tag.id},
    )


def store_tags(tags: Iterable[Tag], conn: sa.Connection) -> None:
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


def like_tags(tags: Iterable[Tag], conn: sa.Connection) -> None:
    for tag in tags:
        update_tag(tag, conn, 1)


def store_recipe(recipe: Recipe, conn: sa.Connection) -> None:
    conn.execute(
        sa.text("INSERT OR IGNORE INTO recipes (id, name) VALUES (:id, :name)"),
        {"id": recipe.metadata.id, "name": recipe.name},
    )

    store_tags(recipe.tags, conn)
    for tag in recipe.tags:
        store_recipe_tag_relationship(recipe.metadata.id, tag.id, conn)


def store_recipe_tag_relationship(
    recipe: Recipe, tag: Tag, conn: sa.Connection
) -> None:
    conn.execute(
        sa.text(
            "INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (:recipe_id, :tag_id)"
        ),
        {"recipe_id": recipe.metadata.id, "tag_id": tag.id},
    )


def store_recipes(recipes: Iterable[Recipe], conn: sa.Connection) -> None:
    for recipe in recipes:
        store_recipe(recipe, conn)


def store_previous_recipe(recipe: Recipe, conn: sa.Connection) -> None:
    conn.execute(
        sa.text("INSERT INTO previous_recipes (recipe_id) VALUES (:recipe_id)"),
        {"recipe_id": recipe.metadata.id},
    )


def store_previous_recipes(recipes: Iterable[Recipe], conn: sa.Connection) -> None:
    for recipe in recipes:
        store_previous_recipe(recipe, conn)


class SimpleRecipe(NamedTuple):
    id: int
    name: str


def get_previous_recipes(conn: sa.Connection) -> list[SimpleRecipe]:
    table = conn.execute(
        sa.text(
            "SELECT recipes.id, recipes.name FROM recipes INNER JOIN previous_recipes ON recipes.id = previous_recipes.recipe_id"
        )
    ).all()

    if not table:
        raise NoDataFoundError()

    return [SimpleRecipe(row.id, row.name) for row in table]


def delete_previous_recipes(conn: sa.Connection) -> None:
    conn.execute(sa.text("DELETE FROM previous_recipes"))


class TableType(StrEnum):
    RECIPES = auto()
    TAGS = auto()
    RECIPE_TAGS = auto()
    DATA = auto()


def print_table(table_type: TableType, conn: sa.Connection) -> None:
    pprint(conn.execute(sa.text(f"SELECT * FROM {table_type}")).all())


class Mode(Enum):
    PREPARE = auto()
    REVIEW = auto()

    @classmethod
    def from_int(cls, i: int) -> Mode:
        if i == 0:
            return cls.PREPARE
        return cls.REVIEW


def get_mode(conn: sa.Connection) -> Mode:
    row = conn.execute(sa.text("SELECT mode FROM data")).first()

    if row is None:
        raise NoDataFoundError()

    return Mode.from_int(row.mode)


def set_mode(mode: Mode, conn: sa.Connection) -> None:
    conn.execute(sa.text("UPDATE data SET mode = :mode"), {"mode": mode.value})


def get_offset(conn: sa.Connection) -> int:
    row = conn.execute(sa.text("SELECT offset FROM data")).first()

    if row is None:
        raise NoDataFoundError()

    return row.offset


def increment_offset(n: int, conn: sa.Connection) -> None:
    """Increments the offset by n."""
    conn.execute(sa.text("UPDATE data SET offset = offset+:n"), {"n": n})


def get_tag_points(conn: sa.Connection) -> dict[int, int]:
    tags = conn.execute(sa.text("SELECT * FROM tags")).all()
    tag_points: dict[int, int] = {}
    for tag in tags:
        tag_points.update({tag.id: tag.likes})

    return tag_points

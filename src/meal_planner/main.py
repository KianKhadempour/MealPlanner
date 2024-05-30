from collections.abc import Collection

import sqlalchemy as sa
from tasty_api import Client
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
            print(f"Your input could not be converted to a{"n" if type_.__name__.startswith(("a", "e", "i", "o", "u")) else ""} {type_.__name__}.")


def get_preferred_recipes() -> list[Recipe]:
    raise NotImplementedError()


def get_preferred_tags(preferred_recipes: Collection[Recipe]) -> list[Tag]:
    preferred_tags: list[Tag] = []
    for recipe in preferred_recipes:
        preferred_tags.extend(recipe.tags)
    
    return preferred_tags

def store_tags(tags: Collection[Tag]) -> None:
    engine = sa.create_engine("sqlite+pysqlite:///:memory:", echo=True)
    
    with engine.connect() as conn:
        conn.execute(sa.text("CREATE TABLE tags (id int PRIMARY KEY, type varchar(255), name varchar(255), display_name varchar(255), likes int)"))
        for tag in tags:
            conn.execute(sa.text("""
            INSERT INTO tags (id, type, name, display_name, likes) 
            VALUES (:id, :type, :name, :display_name, 1)
            ON CONFLICT(id) 
            DO
              UPDATE
              SET likes = likes + 1
        """), {
            'id': tag.id,
            'type': tag.type,
            'name': tag.name,
            'display_name': tag.display_name,
            "likes": 1
        })
        
        result = conn.execute(sa.text("SELECT * FROM tags"))
        print(result.all())


def main() -> None:
    tags = [
        Tag(234, "country", "italian", "Italian"),
        Tag(327, "country", "mediterranean", "Mediterranean"),
        Tag(234, "country", "italian", "Italian"),
        Tag(8, "ingredient", "meatballs", "Meatballs"),
        Tag(42, "ingredient", "parsley", "Parsley"),
        Tag(239, "ingredient", "basil", "Basil"),
        Tag(14, "ingredient", "pepper", "Pepper"),
    ]
    store_tags(tags)
    


if __name__ == "__main__":
    main()

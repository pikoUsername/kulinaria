from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from app.db.repositories.base import TimedModel
from app.db.repositories.helpers import RecipeToIngredient
from app.db.repositories.ingredient.model import Ingredient
from app.db.repositories.tags.model import RecipeTags
from app.db.repositories.text_entities.model import TextEntityRecipe


class Recipe(TimedModel):
    __tablename__ = "recipes"

    name: Mapped[str] = mapped_column(sa.String(90))
    description: Mapped[str] = mapped_column()
    ingredients: Mapped["Ingredient"] = relationship(secondary=RecipeToIngredient)  # M:M
    tags: Mapped[List["RecipeTags"]] = relationship(back_populates="recipe")  # 1:M
    text_entities: Mapped[List["TextEntityRecipe"]] = relationship()  # 1:M

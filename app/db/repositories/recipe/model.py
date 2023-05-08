from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from app.db.repositories.base import TimedModel
from app.db.repositories.category import Category
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
    category_id: Mapped[int] = mapped_column(sa.ForeignKey("categories.id"))
    category: Mapped[Category] = relationship(back_populates="reciepes", cascade="delete-orphan")  # M:1

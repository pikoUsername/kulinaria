from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from app.db.repositories.base import TimedModel
from app.db.repositories.helpers import RecipeToIngredient
from app.db.repositories.ingredient.model import Ingredient


class Recipe(TimedModel):
    __tablename__ = "recipes"

    name: Mapped[str] = mapped_column(sa.String(90))
    description: Mapped[str] = mapped_column()
    ingredients: Mapped["Ingredient"] = relationship(secondary=RecipeToIngredient)  # M:M

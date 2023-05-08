from app.models.schemas.ingredient import IngredientInCreate, IngredientInUpdate
from .model import Ingredient

from app.db.repositories.common import BaseCrud


class IngredientCrud(BaseCrud[Ingredient, IngredientInCreate, IngredientInUpdate]):
    model = Ingredient

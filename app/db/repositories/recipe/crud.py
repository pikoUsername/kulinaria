from app.db.repositories.common import BaseCrud
from app.models.schemas.recipe import RecipeInCreate, RecipeInUpdate

from .model import Recipe


class RecipeCrud(BaseCrud[Recipe, RecipeInCreate, RecipeInUpdate]):
    model = Recipe

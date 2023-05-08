from app.db.repositories.common import BaseCrud

from .model import Recipe


class RecipeCrud(BaseCrud[Recipe, RecipeInCreate, RecipeInUpdate]):
    model = Recipe

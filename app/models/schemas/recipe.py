from typing import Optional, List

from .ingredient import IngredientInCreate
from .rwschema import RWSchema


class RecipeInCreate(RWSchema):
    name: str
    description: str
    ingredients: List[IngredientInCreate]
    category: str
    tags: Optional[List[str]] = []



class RecipeInUpdate(RWSchema):
    pass

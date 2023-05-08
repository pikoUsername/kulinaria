from typing import Optional

from .rwschema import RWSchema


class RecipeInCreate(RWSchema):
    name: str
    description: str
    ingredients: 


class RecipeInUpdate(RWSchema):
    pass

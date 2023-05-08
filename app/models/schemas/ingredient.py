from typing import Optional

from app.models.schemas.rwschema import RWSchema


class IngredientInCreate(RWSchema):
    name: str
    mass: int
    price: int


class IngredientInUpdate(RWSchema):
    name: Optional[str] = None
    mass: Optional[int] = None
    price: Optional[int] = None

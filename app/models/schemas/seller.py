from pydantic import Field

from .rwschema import RWSchema


class SellerInCreate(RWSchema):
    country: str
    name: str = Field(..., max_length=52)

from typing import Tuple, Optional

from .rwschema import RWSchema


class ProductSellerInResponse(RWSchema):
    link: str
    price: int
    name: str
    description: str
    where_name: str
    where: Tuple[float, float] = None


class ProductSellerInCreate(RWSchema):
    description: str = ""
    name: str = None
    where_name: str
    price: int
    where: Optional[Tuple[float, float]] = None
    link: str

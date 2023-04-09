from typing import Tuple, Optional

from .rwschema import RWSchema


class ProductSellerInResponse(RWSchema):
    link: str
    price: int
    name: str
    description: str
    where_name: str


class ProductSellerInCreate(RWSchema):
    product_id: int
    seller_id: int
    description: str
    name: str
    where_name: str
    where: Optional[Tuple[float, float]] = None
    link: str

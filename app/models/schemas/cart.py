from typing import List

from .product import ProductInResponse
from .rwschema import RWSchema


class CartListInResponse(RWSchema):
    products: List[ProductInResponse] = []

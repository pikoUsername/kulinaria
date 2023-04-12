from typing import List

from .rwschema import RWSchema
from ..domain import ProductSellerInDB


class CartListInResponse(RWSchema):
    products: List[ProductSellerInDB] = []

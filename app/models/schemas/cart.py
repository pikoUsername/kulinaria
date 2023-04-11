from typing import List

from .rwschema import RWSchema
from ..domain import ProductSellerInDB


class FavouriteListInResponse(RWSchema):
    products: List[ProductSellerInDB] = []

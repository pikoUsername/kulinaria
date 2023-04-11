from typing import List

from .pagination import PaginatedResponse
from ..domain import ProductInDB


class PaginatedCategoryListResponse(PaginatedResponse):
    products: List[ProductInDB]
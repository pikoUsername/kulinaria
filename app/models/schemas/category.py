from typing import List, Optional

from .pagination import PaginatedResponse
from ..domain import ProductInDB
from .rwschema import RWSchema


class PaginatedCategoryListResponse(PaginatedResponse):
    products: List[ProductInDB]


class CategoryInCreate(RWSchema):
    name: str
    slug: Optional[str] = ''

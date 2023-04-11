from typing import Optional, List

from .rwschema import RWSchema


class SearchRequest(RWSchema):
    name: Optional[str] = ""
    price_base: Optional[int] = None
    price_end: Optional[int] = None
    rating: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

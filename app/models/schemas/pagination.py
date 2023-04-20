from pydantic import Field

from .rwschema import RWSchema


class PaginationInfo(RWSchema):
    current_index: int = Field(0)
    for_page: int


class PaginatedResponse(RWSchema):
    page_count: int
    for_page: int
    result_len: int


from .rwschema import RWSchema


class ReviewInCreate(RWSchema):
    rating: int
    content: str
    author_id: int 

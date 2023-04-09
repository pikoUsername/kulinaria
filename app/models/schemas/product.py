from typing import List, Optional

from .rwschema import RWSchema

from app.models.domain import CommentInDB
from app.models.domain import SellerInDB
from app.models.domain import TagsInDB
from app.models.domain import TextEntitiesInDB
from app.models.domain import ReviewInDB
from ..domain.seller import ProductSellerInDB


class ProductInResponse(RWSchema):
	name: str
	sellers: List[ProductSellerInDB] = []
	comments: List[CommentInDB] = []
	tags: List[TagsInDB] = []
	watches: int = 0
	description: str
	text_entities: List[TextEntitiesInDB] = []


class ProductInCreate(RWSchema):
	name: str
	slug: str
	sellers: List[ProductSellerInDB]
	tags: List[TagsInDB]
	description: str


class ProductInUpdate(RWSchema):
	name: Optional[str] = None
	description: Optional[str] = None
	tags: List[TagsInDB] = []
	reviews: List[ReviewInDB] = []
	text_entities: List[TextEntitiesInDB] = []
	comments: List[CommentInDB] = []
	is_hidden: Optional[bool] = None

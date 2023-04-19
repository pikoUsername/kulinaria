from typing import List, Optional

from .product_seller import ProductSellerInCreate
from .rwschema import RWSchema

from app.models.domain import CommentInDB, ProductInDB
from app.models.domain import SellerInDB
from app.models.domain import TagsInDB
from app.models.domain import TextEntitiesInDB
from app.models.domain import ReviewInDB
from .tags import TagsInCreate
from ..domain.seller import ProductSellerInDB


class ProductInResponse(RWSchema):
	name: str
	slug: str
	sellers: List[ProductSellerInDB] = []
	comments: List[CommentInDB] = []
	tags: List[TagsInDB] = []
	watches: int = 0
	rating: Optional[float] = 0.0
	description: str
	text_entities: List[TextEntitiesInDB] = []


class ProductInCreate(RWSchema):
	name: str
	slug: str
	sellers: List[ProductSellerInCreate]
	tags: List[TagsInCreate]
	category: str
	description: str


class ProductInUpdate(RWSchema):
	name: Optional[str] = None
	description: Optional[str] = None
	tags: List[TagsInDB] = []
	reviews: List[ReviewInDB] = []
	text_entities: List[TextEntitiesInDB] = []
	comments: List[CommentInDB] = []
	is_hidden: Optional[bool] = None


class ProductListsInResponse(RWSchema):
	products: List[ProductInDB]
	size: int

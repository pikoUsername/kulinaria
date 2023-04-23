from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional

from pydantic import Field

from ..common import IDModelMixin, DateTimeModelMixin
from .rwmodel import RWModel


if TYPE_CHECKING:
	from .category import CategoryInDB
	from .comments import CommentInDB
	from .seller import ProductSellerInDB
	from .tag import TagsInDB
	from .text_entities import TextEntitiesInDB


class ProductInDB(IDModelMixin, DateTimeModelMixin, RWModel):
	name: str = Field(max_length=92)
	slug: str = Field(max_length=126)
	sellers: List[ProductSellerInDB] = []
	comments: List[CommentInDB] = []
	tags: Optional[List[TagsInDB]] = []
	rating: Optional[float] = Field(default=0.0)
	category: Optional[CategoryInDB] = None
	watches: int = 0
	description: str = ""
	text_entities: List[TextEntitiesInDB] = []
	is_hidden: bool = False

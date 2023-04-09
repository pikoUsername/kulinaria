from __future__ import annotations
from typing import TYPE_CHECKING, List

from pydantic import Field

from ..common import IDModelMixin, DateTimeModelMixin
from .rwmodel import RWModel


if TYPE_CHECKING:
	from .comments import CommentInDB
	from .seller import ProductSellerInDB
	from .tag import TagsInDB
	from .text_entities import TextEntitiesInDB


class ProductInDB(IDModelMixin, DateTimeModelMixin, RWModel):
	name: str = Field(max_length=92)
	sellers: List[ProductSellerInDB] = []
	comments: List[CommentInDB] = []
	tags: List[TagsInDB] = []
	watches: int
	description: str
	text_entities: List[TextEntitiesInDB] = []

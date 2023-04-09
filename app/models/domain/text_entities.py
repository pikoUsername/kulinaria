from pydantic import HttpUrl

from .rwmodel import RWModel
from app.services.enums import TextEntitiesTypes
from ..common import IDModelMixin, DateTimeModelMixin


class TextEntitiesInDB(IDModelMixin, DateTimeModelMixin, RWModel):
	type: TextEntitiesTypes
	url: HttpUrl = ""
	offset: int
	length: int


class TextEntityProductInDB(TextEntitiesInDB):
	product_id: int


class TextEntityCommentInDB(TextEntitiesInDB):
	comment_id: int


class TextEntityUserInDB(TextEntitiesInDB):
	user_id: int

from pydantic import HttpUrl

from .rwmodel import RWModel
from app.services.enums import TextEntitiesTypes
from ..common import IDModelMixin, DateTimeModelMixin


class TextEntitiesInDB(IDModelMixin, DateTimeModelMixin, RWModel):
	__tablename__ = "text_entities"

	type: TextEntitiesTypes
	url: HttpUrl = ""
	offset: int
	length: int

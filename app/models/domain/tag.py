import typing

from pydantic import Field

from .rwmodel import RWModel
from ..common import IDModelMixin, DateTimeModelMixin


class TagsInDB(IDModelMixin, DateTimeModelMixin, RWModel):
	name: str = Field(max_length=100)
	short_description: str = Field(max_length=100)
	sub_tags: typing.List["TagsInDB"] = []
	parent_tag_id: typing.Optional[int]

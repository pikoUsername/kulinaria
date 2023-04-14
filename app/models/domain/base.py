from __future__ import annotations
from typing import List

from pydantic import Field

from app.models.common import IDModelMixin, DateTimeModelMixin

from app.models.domain.text_entities import TextEntitiesInDB


class CommentSection(IDModelMixin, DateTimeModelMixin):
	# author: User
	author_id: int
	content: str = Field(max_length=256)
	text_entities: List[TextEntitiesInDB] = []
	likes: int = 0

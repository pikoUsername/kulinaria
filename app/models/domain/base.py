from __future__ import annotations
from typing import List, ForwardRef

from pydantic import Field, BaseModel

from app.models.common import IDModelMixin, DateTimeModelMixin

from app.models.domain.text_entities import TextEntitiesInDB
# from app.models.domain.users import User


class CommentSection(IDModelMixin, DateTimeModelMixin):
	# author: User
	author_id: int
	content: str = Field(max_length=256)
	text_entities: List[TextEntitiesInDB] = []
	likes: int = 0


def resolve_forward_refs(models: dict) -> None:
	for k, model in models.items():
		if isinstance(model, BaseModel):
			for key, value in model.__fields__.items():
				if isinstance(value.annotation, ForwardRef):
					value.annotation = models[value.annotation.__forward_arg__]

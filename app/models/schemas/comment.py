from typing import Optional

from .rwschema import RWSchema

from app.models.domain import CommentInDB


class CommentInCreate(RWSchema):
	author_id: int
	content: str
	parent_comment_id: int


class CommentInUpdate(RWSchema):
	author_id: int
	content: Optional[str] = None


class CommentInResponse(CommentInDB):
	pass

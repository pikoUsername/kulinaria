from typing import List, Optional

from .base import CommentSection
from .rwmodel import RWModel


class CommentInDB(CommentSection, RWModel):
	child_comments: List["CommentInDB"] = []
	parent_comment_id: Optional[int] = None

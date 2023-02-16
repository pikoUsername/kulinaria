from pydantic import Field

from .rwmodel import RWModel
from .text_entities import TextEntitiesInDB
import app.models.domain.users
from ..common import IDModelMixin, DateTimeModelMixin


class CommentInDB(IDModelMixin, DateTimeModelMixin, RWModel):
	author: "users.UserInDB"
	author_id: int
	content: str = Field(max_length=256)
	text_entities: list[TextEntitiesInDB] = []

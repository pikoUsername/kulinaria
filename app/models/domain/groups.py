from __future__ import annotations
from typing import List, TYPE_CHECKING

from pydantic import Field

from .rwmodel import RWModel
from app.models.common import IDModelMixin, DateTimeModelMixin


if TYPE_CHECKING:
	from app.models.domain.users import User
	from app.models.domain.perms import Permissions


class Groups(RWModel):
	name: str = Field(...)
	users: List[User] = []
	permissions: List[Permissions] = []


class GroupInDB(Groups, IDModelMixin, DateTimeModelMixin):
	pass

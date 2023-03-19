from typing import TYPE_CHECKING, List

import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped

from app.db.repositories.base import BaseModel
from app.db.repositories.helpers import UserToGroups, PermissionsToGroups

if TYPE_CHECKING:
	from app.db.repositories.models import Permissions, Users


class Groups(BaseModel):
	__tablename__ = "groups"

	permissions: Mapped[List["Permissions"]] = relationship(secondary=PermissionsToGroups)  # M:M
	name = sa.Column(sa.String(125), primary_key=True)
	users: Mapped[List["Users"]] = relationship(secondary=UserToGroups)  # M:M

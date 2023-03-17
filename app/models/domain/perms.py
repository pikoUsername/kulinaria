from pydantic import Field

from app.models.common import IDModelMixin
from app.models.domain.rwmodel import RWModel


class Permissions(RWModel):
	name: str = Field(...)
	code: str = Field(...)


class PermissionsInDB(IDModelMixin, Permissions):
	pass

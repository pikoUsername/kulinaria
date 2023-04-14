from pydantic import Field

from app.models.common import IDModelMixin, DateTimeModelMixin
from app.models.domain.rwmodel import RWModel



class PermissionsInDB(IDModelMixin, DateTimeModelMixin, RWModel):
	name: str = Field(...)
	code: str = Field(...)

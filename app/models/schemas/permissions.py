from pydantic import Field

from app.models.schemas.rwschema import RWSchema


class PermissionInCreate(RWSchema):
	name: str = Field(...)
	code: str = Field(...)

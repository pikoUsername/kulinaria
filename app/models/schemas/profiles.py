from pydantic import BaseModel

from app.models.domain import Profile


class ProfileInResponse(BaseModel):
	profile: Profile

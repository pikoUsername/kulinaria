from typing import Optional

from app.models.common import IDModelMixin, DateTimeModelMixin
from app.models.domain.rwmodel import RWModel


class Profile(RWModel, IDModelMixin, DateTimeModelMixin):
	username: str
	bio: str = ""
	image: Optional[str] = None
	is_deactivated: bool = False
	is_stuff: bool = False

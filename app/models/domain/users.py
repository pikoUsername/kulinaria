from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from pydantic import Field

from app.models.common import DateTimeModelMixin, IDModelMixin
from app.models.domain.rwmodel import RWModel
from app.services import security

if TYPE_CHECKING:
	from app.models.domain.groups import GroupInDB
	from app.models.domain.perms import PermissionsInDB
	from app.models.domain.seller import SellerInDB
	from app.models.domain.product_lists import ProductListInDB


class User(RWModel):
	username: str
	email: str
	bio: Optional[str] = ""
	image: Optional[str] = None
	lastname: Optional[str] = ""
	address: Optional[str] = ""
	is_deactivated: bool = False
	product_lists: List[ProductListInDB] = []
	phone_number: Optional[str] = ""
	is_stuff: bool = False
	last_online: datetime = Field(default_factory=datetime.now)


class UserInDB(IDModelMixin, DateTimeModelMixin, User):
	permissions: List[PermissionsInDB] = []
	seller: SellerInDB = None
	groups: List[GroupInDB] = []
	salt: str = ""
	encrypted_password: str = ""

	def check_password(self, password: str) -> bool:
		return security.verify_password(self.salt + password, self.encrypted_password)

	def change_password(self, password: str) -> None:
		self.salt = security.generate_salt()
		self.encrypted_password = security.get_password_hash(self.salt + password)

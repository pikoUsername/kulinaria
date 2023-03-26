import datetime
import uuid
from typing import List, Set, Optional, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.db.repositories.base import BaseModel
from app.db.repositories.helpers import UserToGroups
from app.services.security import verify_password, get_password_hash, generate_salt

if TYPE_CHECKING:
	from app.db.repositories.permissions import Permissions
	from app.db.repositories.groups import Groups
	from app.db.repositories.seller import Seller
	from app.db.repositories.product_list import ProductLists


class Users(BaseModel):
	__tablename__ = "users"

	username = sa.Column(
		sa.String(255), index=True, primary_key=True)
	uuid = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	lastname = sa.Column(sa.String(255))
	fullname = sa.Column(sa.String(255))  # format: {surname} {name}
	last_online = sa.Column(sa.DateTime(), server_default=func.now())
	email = sa.Column(sa.String(320), index=True, nullable=False)
	is_stuff: Mapped[bool] = mapped_column(default=False)
	image_url = sa.Column(sa.String(256))
	bio = sa.Column(sa.String(256))
	address = sa.Column(sa.String(256))
	encrypted_password = sa.Column(sa.String(300), nullable=False)
	salt = sa.Column(sa.String(256), nullable=False)
	permission_id: Mapped[int] = mapped_column(sa.ForeignKey('permissions.id'), nullable=False)
	permission: Mapped["Permissions"] = relationship(lazy='selectin')  # one to one
	groups: Mapped[List["Groups"]] = relationship(
		back_populates="users",
		secondary=UserToGroups,
		lazy='selectin',
	)  # M:M
	seller_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey("sellers.id"))
	seller: Mapped[Optional["Seller"]] = relationship(uselist=False, foreign_keys="Seller.user_id")  # 1:1
	is_deactivated: Mapped[Optional[bool]] = mapped_column()
	product_lists: Mapped[List["ProductLists"]] = relationship()  # 1:M
	phone_number = sa.Column(sa.String(18))

	def __init__(self, password=None, password_hash=None, salt=None, **kwargs) -> None:
		if salt is None:
			salt = generate_salt()
		self.salt = salt
		if password_hash is None and password is not None:
			password_hash = get_password_hash(self.salt + password)

		super().__init__(encrypted_password=password_hash, **kwargs)

	def change_fullname(self, surname: str, name: str) -> None:
		self.fullname = f"{surname} {name}"

	def change_name(self, username: str) -> None:
		"""
		Изменяет только lastname так как username является ID юзера
		"""
		if not self.lastname:
			self.lastname = username
		self.lastname = username

	@property
	def password(self) -> None:
		raise AttributeError("Password is write only")

	@password.setter
	def password(self, password: str) -> None:
		self.encrypted_password = get_password_hash(self.salt + password)

	def verify_password(self, password: str) -> bool:
		return verify_password(self.salt + password, self.encrypted_password)

	async def update_last_online(self) -> None:
		self.last_online = datetime.datetime.now()

	def get_group_perms(self) -> Set[str]:
		result: Set[str] = set()
		# i don't know how it will affect performance
		for group in self.groups:
			for perm in group.permissions:
				perms = perm.code.split()
				if perms:
					result.add(*perms)

		return result

	def get_permissions(self) -> Set[str]:
		result = set()

		perms = self.permission.code.split()
		if perms:
			result.add(*perms)

		return result

	def get_all_permissions(self) -> Set[str]:
		return {
			*self.get_group_perms(),
			*self.get_permissions(),
		}

	def check_permissions(self, code: str) -> bool:
		"""
		Format: {model_name}_{permissions}
		"""
		if self.is_stuff:
			return True
		perms = self.get_all_permissions()
		return code in perms

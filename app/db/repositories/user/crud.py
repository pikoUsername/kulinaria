from typing import Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.common import BaseCrud
from app.models.domain import User
from app.models.schemas.users import UserInCreate, UserInUpdate
from app.services.enums import GlobalGroups, GlobalPermissions
from app.services.security import get_password_hash, verify_password

from .model import Users


__all__ = "UserCrud",

from ..groups import GroupsCRUD
from ..permissions import PermissionsCrud


class UserCrud(BaseCrud[Users, UserInCreate, UserInUpdate]):
	model = Users

	@classmethod
	async def get_by_email(cls, db: AsyncSession, email: str) -> Optional[Users]:  # noqa
		result = await db.execute(
			sa.select(Users).where(Users.email == email))
		return result.scalar()

	@classmethod
	async def get_by_username(cls, db: AsyncSession, username: str) -> Optional[Users]:
		result = await db.execute(
			sa.select(cls.model).where(Users.username == username))
		return result.scalar()

	@classmethod
	async def update_user(cls, db: AsyncSession, schema_user: User, current_user: UserInUpdate) -> Users:
		if isinstance(current_user, dict):
			update_data = current_user
		else:
			update_data = current_user.dict(exclude_unset=True)
		if update_data["password"]:
			hashed_password = get_password_hash(update_data["password"])
			del update_data["password"]
			update_data["password_hash"] = hashed_password
		db_user = await cls.get_by_email(db, schema_user.email)
		return await super().update(db, db_obj=db_user, obj_in=update_data)

	@classmethod
	async def authenticate(cls, db: AsyncSession, *, email: str, password: str) -> Optional[Users]:
		user = await cls.get_by_email(db, email=email)
		if not user:
			return None
		if not verify_password(password, user.hashed_password):
			return None
		return user

	@classmethod
	async def create(cls, db: AsyncSession, obj_in: UserInCreate) -> Users:
		group = await GroupsCRUD.get_by_kwargs(db, name=GlobalGroups.default_user.name)
		perm = await PermissionsCrud.get_by_kwargs(db, name=GlobalPermissions.anonymous.name)
		user = await super().create_with_relationship(
			db,
			obj_in,
			groups=[group],
			permission=perm,
			product_lists=[],
		)

		return user

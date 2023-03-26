import enum
from typing import Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.common import BaseCrud
from app.models.domain import GroupInDB, Groups as DomainGroups
from app.db.repositories.permissions import PermissionsCrud

from .model import Groups
from ..user import Users


class GroupsCRUD(BaseCrud[Groups, DomainGroups, GroupInDB]):
	model = Groups

	@classmethod
	async def create_default(cls, db: AsyncSession, group_enum: enum.Flag) -> Tuple[Groups, bool]:
		"""
		ONLY used by events.create_default_permissions
		and in future will be used in testing purposes.

		:param db: session
		:param group_enum: value of the GlobalGroups enum
		:return:
		"""
		does_not_exists_err = "permissions with name: {name} does not exists"

		if " " in group_enum.value and len(group_enum.value.split()) > 1:
			# better don't look at this...
			# permissions split up by spaces
			permission_names = group_enum.value.split()
			perms = []

			for name in permission_names:
				_temp = await PermissionsCrud.get_by_kwargs(db, name=name)
				if not _temp:
					raise ValueError(does_not_exists_err.format(name=group_enum.value))
				perms.append(_temp)
		else:
			perms = await PermissionsCrud.get_by_kwargs(db, name=group_enum.value.strip(" "))
			if not perms:
				raise ValueError(does_not_exists_err.format(name=group_enum.value))
			perms = [perms]

		group_mdl = GroupInDB(
			name=group_enum.name,
			users=[],
		)

		return await GroupsCRUD.get_or_create_with_rel(db, group_mdl, permissions=perms, id_name="name")

	@classmethod
	async def get_any_group_by_name(
		cls,
		db: AsyncSession,
		user: Users,
		group_name: str
	) -> Groups:  # it's very bad design
		stmt = select(Users).where(user.groups.any(Groups.name == group_name))
		group = await db.scalar(stmt)
		return group

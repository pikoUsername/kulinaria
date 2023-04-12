import typing
from typing import Type

from fastapi import Depends, HTTPException, params
import sqlalchemy as sa
from loguru import logger
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN

from app.api.dependencies.database import get_connection
from app.db.repositories.user import Users
from app.api.dependencies.authentication import get_current_user_authorizer
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.db.repositories.groups import Groups, GroupsCRUD
from app.db.repositories.control import AccessControl
from app.resources import strings


class CheckPermission(params.Depends):
	__slots__ = "permissions", "model", "_access_control", "group", "_perm_code", "admin_only"

	def __init__(
		self,
		permission: str,
		model: typing.Union[str, Type[sa.Table]] = None,
		group: typing.Union[str, Groups] = None,
		admin_only: bool = False,
	) -> None:
		"""
		:param permission: could be split by spaces
		:param model: init method takes table name and
		formates it into permission string that uses
		:param group: takes name of group, or can be a group name string
		"""
		if isinstance(model, sa.Table):
			model = getattr(model, "__tablename__") or model.__name__
		self.model = model
		self._access_control = AccessControl(self.model)
		if permission == "*":
			self.permissions = self._access_control.all()
		self.permissions = permission.split()

		self._perm_code = self._access_control.format(*self.permissions)
		if isinstance(group, Groups):
			group = group.name
		else:
			group = group
		self.group = group
		self.admin_only = admin_only

		super().__init__(dependency=self.__call__)

	async def __call__(
		self,
		session: AsyncSession = Depends(get_connection),
		user: Users = Depends(get_current_user_authorizer(required=True)),
		settings: AppSettings = Depends(get_app_settings),
	) -> None:
		"""
		Will raise HTTPForbidden if user permissions not enough to use particular route

		* Note: for frontend part, if user is not authed and has anonymous status
		        then redirect user to login page, and save origin url somewhere

		:param session:
		:param user:
		:param settings:
		:return:
		"""
		if settings.debug:
			return
		not_enough_permissions = HTTPException(
			status_code=HTTP_403_FORBIDDEN,
			detail=strings.NOT_ENOUGH_PERMISSIONS,
		)
		if self.admin_only and not user.is_stuff:
			raise not_enough_permissions
		if self.group:
			group = await GroupsCRUD.get_any_group_by_name(session, user, self.group)
			if not group:
				raise not_enough_permissions
			if group.name != self.group:
				raise not_enough_permissions

		if not user.check_permissions(" ".join(self._perm_code)):
			raise not_enough_permissions

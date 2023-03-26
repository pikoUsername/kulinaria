import json
from typing import List, Dict

from loguru import logger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.groups import GroupsCRUD
from app.db.repositories.permissions import PermissionsCrud
from app.models.domain import Permissions as DomainPermission, Groups
from app.db.repositories.control import CONTROL_LIST
from app.db.engine import get_meta


def create_acl(file: str, session: AsyncSession) -> None:
    """
    Этот сервис(да я ебал) запускается перед запуском основного приложения
    И её цель это чтение acl_file-а и сериализации их в Permissions, и Groups моделек
    После этого, этот результат принимает другая функция которая кладет все эти группы
    и пермишшины в базу данных.

    дополнение acl_file-a является json

    Остутвуют тесты! Не используйте пока что
    """
    with open(file, "r", encoding="utf8") as f:
        data = json.load(f)

    logger.info("Creating ACL objects...")
    meta = get_meta()
    tables = meta.sorted_tables
    tables = [table.name for table in tables]
    dto = _AclValidator(data, tables).validate()
    executor = _AclExecutor(session)
    await executor.execute(dto)


class AclDecodeError(Exception):
    pass


class _AclData(BaseModel):
    permissions: List[DomainPermission]
    groups: List[Groups]


class _AclValidator:
    """
    Формат:
    {
        "permissions": {<name>: <code>}
        "groups": {<name>: [<permissions.name>]}
    }

    Валидирует, и проверяет на ошибочные данные
    Связывает Groups, и заменяет permissions.name на сами permissions
    """
    def __init__(self, data: dict, tables: List[str]) -> None:
        self.data = data
        self.tables = set(tables)
        self._permissions: List[DomainPermission] = []
        self._groups: List[Groups] = []

    def _construct_permissions(self, raw_perms: Dict[str, str]) -> List[DomainPermission]:
        if not isinstance(raw_perms, dict):
            raise AclDecodeError("permissions is not dict")
        permissions = []

        for key, value in raw_perms.items():
            codes = value.split()
            for code in codes:
                table, access = code.split("_")
                if table not in self.tables:
                    raise AclDecodeError(f"Table is not valid, table - {table}")
                if access not in CONTROL_LIST:
                    raise AclDecodeError(f"check out this permission: {key}")
            permission = DomainPermission(
                name=key,
                code=value
            )
            permissions.append(permission)

        return permissions

    def _construct_groups(self, raw_groups: Dict[str, str]) -> List[Groups]:
        if not isinstance(raw_groups, dict):
            raise AclDecodeError("Groups is not dict")

        groups = []
        permissions = self._permissions
        if not permissions:
            # yeah, it's not stateless
            raise ValueError("construct_groups used before construct_permissions")

        for group_name, names in raw_groups.items():
            if not isinstance(names, list):
                raise AclDecodeError("group permission names are not list")
            perms = []
            for permission in self._permissions:
                if permission.name in names:
                    perms.append(permission)

            if (not perms and len(names) != 0) or (len(perms) != len(names)):
                raise AclDecodeError(
                    f"Group permission names are not correct, perm list: {names}"
                )

            group = Groups(
                name=group_name,
                permissions=perms,
            )
            groups.append(group)

        return groups

    def validate(self) -> _AclData:
        self._permissions = self._construct_permissions(self.data["permissions"])
        raw_groups = self.data["groups"]
        self._groups = self._construct_groups(raw_groups)

        return _AclData(
            permissions=self._permissions,
            groups=self._groups,
        )


class _AclExecutor:
    """
    Использование:
    AclExecutor(session).execute(data)
    """
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, data: _AclData) -> None:
        """
        Кладет все данные в data в базу данных
        """
        db = self.session
        tx = None
        if not db.in_transaction():
            tx = db.begin()
            await tx.start()

        permissions = data.permissions
        permissions = await PermissionsCrud.create_list(db, permissions)
        try:
            for group in data.groups:
                _temp_perms = []
                for perm in permissions:
                    for perm_model in data.permissions:
                        if perm.name == perm_model.name:
                            _temp_perms.append(perm)
                _, created = await GroupsCRUD.create_with_relationship(
                    db,
                    group,
                    permissions=_temp_perms,
                    users=[]
                )
                if created:
                    logger.info(f"Group {group.name} has been created")
        except Exception:
            if tx:
                await tx.rollback()
            raise
        else:
            if tx:
                await tx.commit()

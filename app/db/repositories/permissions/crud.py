from app.db.repositories.common import BaseCrud
from app.db.repositories.permissions.model import Permissions

from app.models.domain import PermissionsInDB
from app.models.schemas.permissions import PermissionInCreate


class PermissionsCrud(BaseCrud[Permissions, PermissionInCreate, PermissionsInDB]):
	model = Permissions

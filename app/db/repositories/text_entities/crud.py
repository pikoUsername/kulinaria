from typing import List, Type, TypeVar, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import TextEntitiesInDB
from app.services.filler import fill
from ..common import BaseCrud

from .model import TextEntity


T = TypeVar("T", bound=TextEntity)


class TextEntitiesCRUD(
	BaseCrud[TextEntity, TextEntitiesInDB, TextEntitiesInDB]
):
	model = TextEntity

	@classmethod
	async def create_list(
			cls,
			db: AsyncSession,
			obj_in: List[TextEntitiesInDB],
			**options: Any,
	) -> List[T]:
		typ: Type[T] = options.pop("typ")
		if typ.__abstract__ and not hasattr(typ, '__tablename__'):
			raise ValueError("Type is not correct")
		ret_models = []

		for obj in obj_in:
			model_obj = fill(obj, typ)
			db.add(model_obj)
			ret_models.append(model_obj)

		return ret_models

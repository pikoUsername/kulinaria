from typing import TypeVar, Type, List, Iterable, Dict, Any

import sqlalchemy as sa
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)
ST = TypeVar("ST", bound=sa.Table)


def convert_db_obj_to_model(db_obj: ST, model: Type[T]) -> T:
	return model.from_orm(db_obj)


def convert_list_obj_to_model(objects: List[ST], model: Type[T]) -> Iterable[T]:
	models = []

	for obj in objects:
		models.append(model.from_orm(obj))

	return models


def extract_default_value_from_db_obj(db_obj: ST) -> Dict[str, Any]:
	"""
	Extracts created_at, updated_at, id from db obj

	:param db_obj:
	:return:
	"""
	return {
		"id": db_obj.id,
		"created_at": db_obj.created_at,
		"updated_at": db_obj.updated_at,
	}


def remove_default_values_db_obj(db_obj: T) -> T:
	return db_obj.copy(exclude={"id", "created_at", "updated_at"})


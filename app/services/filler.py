from abc import ABCMeta, abstractmethod
from typing import Optional, TypeVar, List, Any, Type, ForwardRef, Union

import sqlalchemy as sa
from sqlalchemy.orm.attributes import QueryableAttribute
from pydantic import BaseModel
from pydantic.fields import ModelField
from fastapi.encoders import jsonable_encoder
from loguru import logger

from .mixins import ContextInstanceMixin


T = TypeVar("T", bound=BaseModel)
ST = TypeVar("ST", bound=Union[dict, sa.Table])
FT = TypeVar("FT", bound=ModelField)


class ModelsFillerInterface:
	"""
	Для совместимости с другими фрейморвками, и простым sql
	"""
	@abstractmethod
	def fill(self, model: T, db_obj: ST) -> T:
		pass

	@abstractmethod
	def configure(self, *args, **kwargs) -> None:
		pass


class ModelsFiller(ContextInstanceMixin["ModelsFiller"], ModelsFillerInterface):
	"""
	Используется как резолвер под моделей в моделях pydantic
	находит через метадату таблицу, валидирует, и выдает результат

	Можно использвать как глобальную переменную, так и локальную

	model = GroupsInDB(
		permissions=perms,
		users=[]
		name="",
	)

	SubModelsResolver(meta).resolve(model)

	"""
	def __init__(self, meta: Optional[sa.MetaData] = None) -> None:
		if meta:
			self._tables = meta.tables
		self.meta = meta
		
		super(ModelsFiller, self).__init__()

	def configure(self, *args, **kwargs) -> None:
		meta = kwargs.pop("meta")
		self.meta = meta
		self._tables = self._tables

	def normalize_model_name(self, name: str) -> str:
		"""
		очищает строку для проверки от не нужного

		:param name:
		:return:
		"""
		s = name.lower()
		i = s.find("indb")
		if i == -1:
			return name
		return name[:i]

	def find_table_by_name(self, name: str) -> sa.Table:
		"""
		If your table name is special like TextEntities
		then write it down into __tablename__ field

		Если имя модели заканчивается 's' то оно будет возвращать это значение
		При уникальном случае просто поставьте __tablename__ на нужное значение

		:param name:
		:return:
		"""
		n = name.lower() + "s"
		if name.endswith("s"):
			n = name.lower()
		return self.get_table_by_name(n)

	def get_table_by_name(self, name: str) -> sa.Table:
		return self._tables[name]

	def resolve_model_name(self, model: Type[T]) -> sa.Table:
		"""
		находит модельку по self._tables

		:param model:
		:return:
		"""
		name = model.__name__
		if hasattr(model, "__tablename__"):
			return self.get_table_by_name(model.__tablename__)
		name = self.normalize_model_name(name)
		return self.find_table_by_name(name)

	def detect_sub_models(self, model: T) -> List[str]:
		result = []
		for key, value in model.__fields__.items():
			if issubclass(value.type_, BaseModel):
				try:
					self.resolve_model_name(value.type_)
				except TypeError as exc:
					raise ValueError("%s is not associated with any tables." % key) from exc
				result.append(key)
		return result

	def validate_relation(self, key: str, db_obj: ST) -> Any:
		"""
		Вызывает еррорку при обнаружении проблемы

		:param key:
		:param db_obj:
		:return:
		"""
		rel = getattr(db_obj, key, None)

		if not rel:
			raise ValueError(
				"wrong configuration, key %s is not associated with any column in table" % key
			)
		if not isinstance(rel, QueryableAttribute) or not rel.class_:
			raise ValueError(
				"column - %s is not any valid relationship" % key
			)
		return rel

	def check_if_iterable(self, field: ModelField) -> bool:
		if field.outer_type_ == field.type_:
			return False
		if isinstance(field.outer_type_, ForwardRef):
			for_ref = field.outer_type_.__forward_arg__.lower()
			seq_list = {"list", "set", "tuple", "sequence", "iterable"}  # very stupid way to check
			# TODO: find a way to evaluate forward ref, without cracky hacks
			for seq in seq_list:
				if seq in for_ref:
					return True
		else:
			if isinstance(field.outer_type_.__origin__, (list, set, tuple)):
				return True
		return False

	def fill(self, model: T, db_obj: ST) -> ST:  # db_obj has to be model object
		"""
		Заполнит до окончания, сделает все абсолютно все
		Предполагается что модель и таблица алхимии АБСОЛЮТНО точные

		:param model:
		:return:
		"""
		for key, field in model.__fields__.items():
			field: ModelField
			if issubclass(field.type_, BaseModel):
				if self.check_if_iterable(field):
					to_iterate = getattr(model, key)
					for val in to_iterate:
						db_rel_f = self._fill_table_data_by_one(db_obj, key, val)
						getattr(db_obj, key).add(db_rel_f)
					continue
				db_rel = self._fill_table_data_by_one(db_obj, key, field)
				getattr(db_obj, key).add(db_rel)

		return db_obj

	def _fill_table_data_by_one(self, db_obj: sa.Table, key: str, field: Union[T, FT]) -> sa.Table:
		"""
		Field.type_ должен соответствовать BaseModel

		Предполагается что модельки абсолютно точно реперезентеруют таблицы

		:param db_obj:
		:param key:
		:param field:
		:return:
		"""
		if isinstance(field, ModelField):
			typ = field.type_
		else:
			typ = type(field)

		table = self.resolve_model_name(typ)
		logger.info(table)
		obj_in_data: dict = jsonable_encoder(field, exclude_unset=True)
		logger.info(type(table))
		sub_main_obj = table(**obj_in_data)  # noqa
		assert self.validate_relation(key, db_obj)
		if self.detect_sub_models(typ):
			self.fill(field, sub_main_obj)

		return sub_main_obj

	def convert_model_to_db_obj(self, obj_in: T) -> sa.Table:
		db_type = self.resolve_model_name(type(obj_in))

		data = jsonable_encoder(obj_in, exclude_unset=True)
		return db_type(**data)  # noqa


def fill_db_obj(model: T, db_obj: Type[ST]) -> ST:
	"""
	является фасадом для ModelsFiller

	Использование:
	db_obj = fill_db_obj(model, cls.table)
	session.add(db_obj)

	:param model:
	:param db_obj:
	:return:
	"""
	filler = ModelsFiller.get_current()
	data = jsonable_encoder(
		model,
		exclude_unset=True,
		exclude=set(filler.detect_sub_models(model)),
	)
	db_obj = db_obj(**data)
	return fill(model, db_obj)


def fill(model: T, db_obj: ST) -> ST:
	filler = ModelsFiller.get_current()

	if not filler.meta:
		raise TypeError("Models filler is not initialized properly")
	return filler.fill(model, db_obj)


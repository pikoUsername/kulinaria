from abc import abstractmethod
from typing import TypeVar, List, Any, Type, ForwardRef, Union

import sqlalchemy as sa
from sqlalchemy.orm.attributes import QueryableAttribute
from pydantic import BaseModel
from pydantic.fields import ModelField
from fastapi.encoders import jsonable_encoder

from .mixins import ContextInstanceMixin
from ..db.repositories.helpers import get_tables

T = TypeVar("T", bound=BaseModel)
ST = TypeVar("ST", bound=Union[dict, Type[sa.Table]])
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

	def __init__(self) -> None:
		self._tables = get_tables()

		self.set_current(self)

	def configure(self):
		pass

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

		if not hasattr(db_obj, key):
			raise ValueError(
				"wrong configuration, key '%s' is not associated with any column in table" % key
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
		:param db_obj:
		:return:
		"""
		relations = {}

		for key, field in model.__fields__.items():
			field: ModelField
			if issubclass(field.type_, BaseModel):
				if self.check_if_iterable(field):
					to_iterate = getattr(model, key)
					for val in to_iterate:
						db_rel_f = self._fill_table_data_by_one(db_obj, key, val)
						if not relations.get(key, None):
							relations[key] = []
						relations[key].append(db_rel_f)
					# _getattr_and_set_list_or_append(db_obj, key, db_rel_f)
					continue
				db_rel = self._fill_table_data_by_one(db_obj, key, field)
				relations[key] = db_rel

		data = jsonable_encoder(
			model,
			exclude_unset=True,
			exclude=set(self.detect_sub_models(model))
		)
		db_obj = db_obj(**data, **relations)

		return db_obj

	def _fill_table_data_by_one(self, db_obj: Type[sa.Table], key: str, field: Union[T, FT]) -> sa.Table:
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
		obj_in_data: dict = jsonable_encoder(field, exclude_unset=True)
		sub_main_obj = table(**obj_in_data)  # noqa
		assert self.validate_relation(key, db_obj)
		if self.detect_sub_models(typ):
			sub_main_obj = self.fill(field, sub_main_obj)

		return sub_main_obj

	def convert_model_to_db_obj(self, obj_in: T) -> sa.Table:
		db_type = self.resolve_model_name(type(obj_in))

		data = jsonable_encoder(obj_in, exclude_unset=True)
		return db_type(**data)  # noqa


class _SqlAlchemyDuplicationResolver:
	"""
	Resolves sqlalchemy duplication error. i.e.:
	sqlalchemy.exc.IntegrityError:
		(sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.UniqueViolationError'>:

	That accrues if object is not fetched one.
	Bounds to ModelsFiller class.
	"""
	def __init__(self, filler: ModelsFiller):
		self._filler = filler

	def resolve(self, db_obj: Type[ST], duplicates: List[str]) -> None:
		"""
		This resolve method actually runs some session queries
		So, count it as another layer that uses Databases,
		and must be heavily tested

		Of course, it gives a LOT of overhead, espacially on user table.
		But hey, it's just expermintal stuff that i do for myself.
		Not anyone can understand what's going on

		After that now you can use the create method as shown below:
		await BaseCrud.create(obj)

		TODO!

		:param db_obj:
		:param duplicates:
		:return:
		"""
		for duplicate in duplicates:
			duplicate_rel = getattr(db_obj, duplicate)
			if duplicate_rel is None:
				pass


def fill(model: T, db_obj: Type[ST]) -> ST:
	filler = ModelsFiller.get_current()

	if not filler._tables:
		raise TypeError("Models filler is not initialized properly")
	return filler.fill(model, db_obj)


def detect_sub_models(model: T) -> List[str]:
	filler = ModelsFiller.get_current()
	return filler.detect_sub_models(model)

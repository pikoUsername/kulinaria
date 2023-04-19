from typing import Generic, TypeVar, List, Union, Dict, Any, Optional, Tuple, Sequence, Type

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import sqlalchemy as sa
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result

from app.db.repositories.base import BaseModel as DBBaseModel
from app.services.filler import fill

ExModelType = TypeVar("ExModelType", bound=DBBaseModel)
ModelType = TypeVar("ModelType", bound=DBBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseCrud(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
	"""
	Provides basic CRUD support system,
	with extra method support - get_multi, create_with_relationship, get_or_create

	Usages:
	Crud.create_with_relationship(CreateSchemaType)

	"""
	model: Type[sa.Table]

	@classmethod
	async def get(cls, db: AsyncSession, id: Any) -> Optional[ModelType]:
		result = await db.scalars(sa.select(cls.model).where(cls.model.id == id))
		result = result.first()
		return result

	@classmethod
	async def get_by_values(
			cls, db: AsyncSession, values: List[Any], key: str = "id"
	) -> Optional[Sequence[ModelType]]:
		stmt = sa.select(cls.model).filter_by(**{key: x for x in values})
		result: Result = await db.execute(stmt)
		return result.all()  # noqa

	@classmethod
	async def get_by_kwargs(
			cls, db: AsyncSession, **kwargs: Any
	) -> Optional[ModelType]:
		stmt = sa.select(cls.model).filter_by(**kwargs)
		result = await db.scalars(stmt)
		result = result.first()
		return result

	@classmethod
	async def get_or_create(
			cls, db: AsyncSession, obj_in: CreateSchemaType, id_name: str = "id"
	) -> Tuple[ModelType, bool]:
		kw = {id_name: getattr(obj_in, id_name)}
		result = await cls.get_by_kwargs(db, **kw)
		if result:
			return result, False
		return await cls.create(db, obj_in.copy()), True

	@classmethod
	async def get_or_create_with_rel(
			cls,
			db: AsyncSession,
			obj_in: CreateSchemaType,
			id_name: str = "id",
			additional_opts: Dict[str, Any] = None,
			**relationships: Union[List[sa.Table], sa.Table],
	) -> Tuple[ModelType, bool]:
		kw = {id_name: getattr(obj_in, id_name)}
		result = await cls.get_by_kwargs(db, **kw)

		if result:
			return result, False

		return await cls.create_with_relationship(
			db,
			obj_in=obj_in.copy(),
			additional_opts=additional_opts,
			**relationships
		), True

	@classmethod
	async def create_list(cls, db: AsyncSession, obj_in: List[CreateSchemaType], **options) -> List[ModelType]:
		ret_models = []
		for obj in obj_in:
			model_obj = fill(obj, cls.model)
			db.add(model_obj)
			ret_models.append(model_obj)
		await db.commit()
		for obj in ret_models:
			await db.refresh(obj)

		return ret_models

	@classmethod
	async def create(cls, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
		db_obj = fill(obj_in, cls.model)
		db.add(db_obj)
		await db.commit()
		await db.refresh(db_obj)
		return db_obj

	@classmethod
	async def create_with_relationship(
			cls,
			db: AsyncSession,
			obj_in: CreateSchemaType,
			additional_opts: Dict[str, Any] = None,
			**relationships: Union[List[sa.Table], sa.Table],
	) -> ModelType:
		obj_in_data: dict = jsonable_encoder(
			obj_in,
			exclude_unset=True,
			exclude=set(relationships.keys()),
		)
		if additional_opts:
			obj_in_data.update(**additional_opts)
		db_obj = cls.model(**obj_in_data)
		for key, value in relationships.items():
			if isinstance(value, (list, tuple, set)) and value is not None:
				rel = getattr(db_obj, key)
				for val in value:
					logger.info(f"{key}: {val.__dict__}")
					rel.append(val)
				continue
			setattr(db_obj, key, value)
		db.add(db_obj)
		await db.commit()
		await db.refresh(db_obj)

		return db_obj

	@classmethod
	async def update(
			cls,
			db: AsyncSession,
			db_obj: ModelType,
			obj_in: UpdateSchemaType
	) -> ModelType:
		logger.info(
			f"Changed object: {cls.model.__tablename__}")
		for key, value in obj_in.dict(exclude={"id"}).items():
			if hasattr(db_obj, key):
				setattr(db_obj, key, value)

		await db.commit()
		await db.refresh(db_obj)
		return db_obj

	@classmethod
	async def delete(cls, db: AsyncSession, id: int) -> ModelType:
		logger.info(
			f"Removed object: {cls.model.__tablename__} from database data.")

		obj = await cls.get(db, id)
		await db.delete(obj)
		await db.commit()
		return obj

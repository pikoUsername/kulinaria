from pydantic import BaseConfig, BaseModel, validator
from sqlalchemy.orm import Query


class RWModel(BaseModel):
	@classmethod
	def get_table_name(cls):
		if hasattr(cls, '__tablename__'):
			return cls.__tablename__
		s = cls.__name__.lower()
		s = s.strip("indb")
		return s.capitalize()

	@validator("*", pre=True)
	def evaluate_lazy_columns(cls, v):
		if isinstance(v, Query):
			return v.all()
		return v

	class Config(BaseConfig):
		orm_mode = True

import sqlalchemy as sa

from app.db.engine import Base


class BaseModel(Base):
	__abstract__ = True

	id = sa.Column(sa.BigInteger, autoincrement=True, index=True, primary_key=True, unique=True)


class TimedModel(BaseModel):
	__abstract__ = True

	created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
	updated_at = sa.Column(sa.DateTime, onupdate=sa.func.now())


class TestBaseModel(BaseModel):
	__abstract__ = True

	def __init__(self, *args, **kwargs):
		# TODO: Make filler here, not outside!
		pass

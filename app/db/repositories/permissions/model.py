import sqlalchemy as sa

from app.db.repositories.base import TimedModel


class Permissions(TimedModel):
	"""
	Все пермишинны будут привязаны к юзеру
	"""
	__tablename__ = "permissions"

	name = sa.Column(sa.String(255), primary_key=True)
	code = sa.Column(sa.String(256), nullable=False)  # format: {model_name}_{permission}

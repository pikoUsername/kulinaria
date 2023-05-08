from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Index
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.db.repositories.base import TimedModel
from app.db.repositories.helpers import TSVector

if TYPE_CHECKING:
	from app.db.repositories.recipe import Recipe


class Tags(TimedModel):
	__abstract__ = True

	name = sa.Column(sa.String(72), nullable=False)
	short_description = sa.Column(sa.String(100))


class RecipeTags(Tags):
	__tablename__ = "product_tags"

	recipe_id: Mapped[int] = mapped_column(sa.ForeignKey("recipes.id"))
	recipe: Mapped["Recipe"] = relationship(back_populates="tags")  # M:1

	ts_vector = sa.Column(TSVector(), sa.Computed(
		"to_tsvector('russian', name || ' ' || short_description)",
		persisted=True))
	__table_args__ = (Index('ix_tag___ts_vector__', ts_vector, postgresql_using='gin'),)

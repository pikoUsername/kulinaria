from typing import List, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.repositories.base import TimedModel

if TYPE_CHECKING:
	from app.db.repositories.models import Users, TextEntityReview
	from app.db.repositories.base import TimedModel


class Reviews(TimedModel):
	"""
	For anything that has rating column
	"""
	__tablename__ = "reviews"

	rating = sa.Column(sa.Integer)
	is_hidden = sa.Column(sa.Boolean, default=False)
	content = sa.Column(sa.String(256), nullable=False)
	product_id: Mapped[int] = mapped_column(sa.ForeignKey('products.id', ondelete="CASCADE"))
	likes: Mapped[int] = mapped_column(default=0)
	author_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"))
	author: Mapped["Users"] = relationship()  # M:1
	text_entities: Mapped[List["TextEntityReview"]] = relationship()  # 1:M

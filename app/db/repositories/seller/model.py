from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.repositories.base import TimedModel

if TYPE_CHECKING:
	from app.db.repositories.models import Products


class Seller(TimedModel):
	"""
	Seller is linked to user model by one relationship
	"""
	__tablename__ = 'sellers'

	rating = sa.Column(sa.Float)  # 5 to 1
	products: Mapped["Products"] = relationship(back_populates="seller")  # 1:M
	country = sa.Column(sa.String(125))
	bio = sa.Column(sa.Text)
	is_activated = sa.Column(sa.Boolean, default=True)
	is_blocked = sa.Column(sa.Boolean, default=False)
	user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"))

from typing import TYPE_CHECKING, List, Optional

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

	name = sa.Column(sa.String(52), primary_key=True)
	rating = sa.Column(sa.Float)  # 5 to 1
	product_seller: Mapped[List["ProductSeller"]] = relationship(back_populates="seller")  # 1:M
	country = sa.Column(sa.String(125))
	is_activated = sa.Column(sa.Boolean, default=True)
	is_blocked = sa.Column(sa.Boolean, default=False)


class ProductSeller(TimedModel):
	__tablename__ = 'product_sellers'

	product: Mapped["Products"] = relationship(cascade="delete", single_parent=True)
	product_id: Mapped[int] = mapped_column(sa.ForeignKey('products.id'))
	seller_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('sellers.id'))
	seller: Mapped[Optional["Seller"]] = relationship(lazy='selectin')
	description: Mapped[str] = mapped_column()
	name = sa.Column(sa.String(100), nullable=False)
	where = sa.Column(sa.ARRAY(sa.Float))  # limited to 2
	where_name = sa.Column(sa.String(52))
	price: Mapped[int] = mapped_column()
	link: Mapped[str] = mapped_column()

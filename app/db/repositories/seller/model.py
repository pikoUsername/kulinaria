from typing import TYPE_CHECKING, List

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

	product_id: Mapped[int] = mapped_column(sa.ForeignKey('products.id'))
	product: Mapped["Products"] = relationship()
	seller_id: Mapped[int] = mapped_column(sa.ForeignKey('sellers.id'))
	seller: Mapped["Seller"] = relationship()
	description: Mapped[str] = mapped_column()
	name = sa.Column(sa.String(100), nullable=False)
	where = sa.Column(sa.ARRAY(sa.Float))  # limited to 2
	where_name = sa.Column(sa.String(52))
	price: Mapped[int] = mapped_column()
	link: Mapped[str] = mapped_column()

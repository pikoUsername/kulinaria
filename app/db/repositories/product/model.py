from typing import List, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.repositories.base import TimedModel
from app.db.repositories.review import Reviews

if TYPE_CHECKING:
	from app.db.repositories.models import Seller, Comments, ProductTags, TextEntityProduct


class Products(TimedModel):
	__tablename__ = "products"

	name = sa.Column(sa.String(92), nullable=False)
	seller: Mapped["Seller"] = relationship(back_populates="products")  # many:1
	seller_id: Mapped[int] = mapped_column(sa.ForeignKey("sellers.id", ondelete="CASCADE"))
	comments: Mapped[List["Comments"]] = relationship()  # 1:many
	tags: Mapped[List["ProductTags"]] = relationship()  # 1:many
	reviews: Mapped[List["Reviews"]] = relationship()  # 1:many
	watches = sa.Column(sa.Integer)
	description = sa.Column(sa.Text)
	text_entities: Mapped[List["TextEntityProduct"]] = relationship()  # 1:many for text
	is_hidden = sa.Column(sa.Boolean, default=False)

from typing import List, TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.repositories.base import TimedModel
from app.db.repositories.category.model import Category
from app.db.repositories.review import Reviews

if TYPE_CHECKING:
	from app.db.repositories.models import ProductSeller, Comments, ProductTags, TextEntityProduct


class Products(TimedModel):
	__tablename__ = "products"

	name = sa.Column(sa.String(92), nullable=False)
	slug = sa.Column(sa.String(126), nullable=False)  # used in URI
	sellers: Mapped[List["ProductSeller"]] = relationship(back_populates="product")  # 1:M
	comments: Mapped[List["Comments"]] = relationship()  # 1:many
	tags: Mapped[List["ProductTags"]] = relationship()  # 1:many
	reviews: Mapped[Optional[List["Reviews"]]] = relationship()  # 1:many
	rating: Mapped[Optional[float]] = mapped_column()
	watches = sa.Column(sa.Integer, default=0)
	category: Mapped["Category"] = relationship(back_populates="products")  # M:1
	category_id: Mapped[int] = mapped_column(sa.ForeignKey("categories.id"))
	description = sa.Column(sa.Text)
	text_entities: Mapped[Optional[List["TextEntityProduct"]]] = relationship()  # 1:many for text
	is_hidden = sa.Column(sa.Boolean, default=False)

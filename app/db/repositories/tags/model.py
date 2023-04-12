from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.db.repositories.base import TimedModel


class Tags(TimedModel):
	__abstract__ = True

	name = sa.Column(sa.String(72))
	short_description = sa.Column(sa.String(100))


class ProductTags(Tags):
	__tablename__ = "product_tags"

	product_id: Mapped[int] = mapped_column(sa.ForeignKey("products.id"))
	# sub_tags: Mapped[Optional["ProductTags"]] = relationship("ProductTags", lazy='selectin')
	# parent_tag_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('product_tags.id'))

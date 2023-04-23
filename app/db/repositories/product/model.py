from typing import List, TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlalchemy import cast, func, Index
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.repositories.base import TimedModel
from app.db.repositories.helpers import ListsToProducts, create_tsvector, TSVector

if TYPE_CHECKING:
    from app.db.repositories.models import ProductSeller, Comments, ProductTags, TextEntityProduct, Category
    from app.db.repositories.product_list import ProductLists
    from app.db.repositories.review import Reviews


class Products(TimedModel):
    __tablename__ = "products"

    name = sa.Column(sa.String(92), nullable=False)
    slug = sa.Column(sa.String(126), primary_key=True)  # used in URI
    sellers: Mapped[List["ProductSeller"]] = relationship(lazy='selectin', back_populates="product")  # 1:M
    comments: Mapped[List["Comments"]] = relationship(lazy='selectin')  # 1:many
    tags: Mapped[List["ProductTags"]] = relationship(lazy='selectin', back_populates="product")  # 1:many
    product_lists: Mapped[List["ProductLists"]] = relationship(secondary=ListsToProducts, lazy='selectin',
                                                               back_populates="products")
    reviews: Mapped[Optional[List["Reviews"]]] = relationship()  # 1:many
    rating = sa.Column(sa.Float, nullable=True)
    watches = sa.Column(sa.Integer, default=0)
    category: Mapped["Category"] = relationship(back_populates="products", lazy='selectin')  # M:1
    category_id: Mapped[int] = mapped_column(sa.ForeignKey("categories.id"))
    description = sa.Column(sa.Text)
    text_entities: Mapped[Optional[List["TextEntityProduct"]]] = relationship(lazy='selectin')  # 1:many for text
    is_hidden = sa.Column(sa.Boolean, default=False)

    # ts_vector = create_tsvector(
    # 	cast(func.coalesce(name, description, slug, ''), postgresql.TEXT)
    # )
    # __table_args__ = (
    # 	Index(
    # 		'idx_product_fts',
    # 		ts_vector,
    # 		postgresql_using='gin'
    # 	),
    # )

    ts_vector = sa.Column(TSVECTOR(), sa.Computed(
        "to_tsvector('russian', name || ' ' || slug || ' ' || description)",
        persisted=True))
    __table_args__ = (Index('ix_video___ts_vector__',
                            ts_vector, postgresql_using='gin'),)

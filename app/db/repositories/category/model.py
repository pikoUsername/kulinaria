from typing import List, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship, Mapped

from app.db.repositories.base import TimedModel

if TYPE_CHECKING:
    from app.db.repositories.product import Products


class Category(TimedModel):
    __tablename__ = "categories"

    name = sa.Column(sa.String(52), primary_key=True)
    slug = sa.Column(sa.String(128))
    # dont change lazy=selectin, otherwise it will load hundreds of products
    products: Mapped[List["Products"]] = relationship(back_populates="category")

    ts_vector = sa.Column(TSVECTOR(), sa.Computed(
        "to_tsvector('russian', name)",
        persisted=True))
    __table_args__ = (Index('ix_category___ts_vector__',
                            ts_vector, postgresql_using='gin'),)

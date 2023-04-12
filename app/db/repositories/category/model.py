from typing import List, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped

from app.db.repositories.base import TimedModel

if TYPE_CHECKING:
    from app.db.repositories.product import Products


class Category(TimedModel):
    __tablename__ = "categories"

    name = sa.Column(sa.String(52), primary_key=True)
    slug = sa.Column(sa.String(128))
    products: Mapped[List["Products"]] = relationship(back_populates="category")

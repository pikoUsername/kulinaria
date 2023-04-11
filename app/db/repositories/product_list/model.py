from typing import List, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.db.repositories.base import TimedModel
from app.db.repositories.helpers import ListsToProducts

if TYPE_CHECKING:
	from app.db.repositories.models import Products


class ProductLists(TimedModel):
	__tablename__ = 'product_lists'

	name = sa.Column(sa.String(52))
	products: Mapped[List["Products"]] = relationship(secondary=ListsToProducts, lazy='selectin')  # M:M
	user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"))

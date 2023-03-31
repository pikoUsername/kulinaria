from typing import List, TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.db.repositories.base import TimedModel


if TYPE_CHECKING:
	from app.db.repositories.models import Users, TextEntityComment


class Comments(TimedModel):
	"""
	Used for products
	"""
	__tablename__ = "comments"

	is_hidden = sa.Column(sa.Boolean, default=False)
	product_id: Mapped[int] = mapped_column(sa.ForeignKey("products.id"))
	content = sa.Column(sa.String(256), nullable=False)
	likes: Mapped[int] = mapped_column(default=0)
	author_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"))
	author: Mapped["Users"] = relationship()  # M:1
	text_entities: Mapped[List["TextEntityComment"]] = relationship()  # 1:M
	parent_comment_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey("comments.id"))
	child_comments: Mapped[Optional[List["Comments"]]] = relationship()  # 1:M

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped

from app.db.repositories.base import TimedModel


class TextEntity(TimedModel):
	"""
	Used for messages, comments, and etc.
	offset uses for define start text entity
	length uses for defining ending of the text entity
	In one message could be a several text entities
	"""
	__abstract__ = True

	type = sa.Column(sa.String(52), nullable=False)
	url = sa.Column(sa.Text)
	offset = sa.Column(sa.Integer, nullable=False)
	length = sa.Column(sa.Integer, nullable=False)


class TextEntityComment(TextEntity):
	__tablename__ = "text_entities_comments"

	comment_id: Mapped[int] = mapped_column(
		sa.ForeignKey("comments.id", ondelete="CASCADE")
	)


class TextEntityReview(TextEntity):
	__tablename__ = "text_entities_reviews"

	review_id: Mapped[int] = mapped_column(
		sa.ForeignKey("reviews.id", ondelete="CASCADE")
	)


class TextEntityUser(TextEntity):
	__tablename__ = "text_entities_users"

	user_id: Mapped[int] = mapped_column(
		sa.ForeignKey("users.id", ondelete="CASCADE")
	)


class TextEntityRecipe(TextEntity):
	__tablename__ = "text_entities_recipes"

	recipe_id: Mapped[int] = mapped_column(
		sa.ForeignKey("recipes.id", ondelete="CASCADE")
	)

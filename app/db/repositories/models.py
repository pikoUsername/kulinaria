from app.db.repositories.base import BaseModel, TimedModel
from app.db.repositories.comments import Comments
from app.db.repositories.groups import Groups
from app.db.repositories.helpers import ListsToProducts, UserToGroups
from app.db.repositories.permissions import Permissions
from app.db.repositories.review import Reviews
from app.db.repositories.tags import Tags, ProductTags
from app.db.repositories.text_entities import (
	TextEntity,
	TextEntityComment,
	TextEntityProduct,
	TextEntityReview,
	TextEntityUser,
)
from app.db.repositories.user import Users
from app.db.repositories.category import Category

# Helper file for alembic
# NOTE: Don't import from anywhere in application to this file directly
# to get tables use app.db.repositories.helpers.get_tables

__all__ = (
	'BaseModel',
	'TimedModel',
	'Reviews',
	'ListsToProducts',
	'UserToGroups',
	'Permissions',
	'Users',
	'Groups',
	'Comments',
	'Category',
	'ProductTags',
	'TextEntity',
	'TextEntityComment',
	'TextEntityProduct',
	'TextEntityUser',
	'TextEntityReview',
	'Tags',
)

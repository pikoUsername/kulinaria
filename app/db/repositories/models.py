from app.db.repositories.comments import Comments
from app.db.repositories.groups import Groups
from app.db.repositories.helpers import ListsToProducts, UserToGroups
from app.db.repositories.permissions import Permissions
from app.db.repositories.product import Products
from app.db.repositories.product_list import ProductLists
from app.db.repositories.review import Reviews
from app.db.repositories.seller import Seller, ProductSeller
from app.db.repositories.tags import Tags, ProductTags
from app.db.repositories.text_entities import (
	TextEntity,
	TextEntityComment,
	TextEntityProduct,
	TextEntityReview,
	TextEntityUser,
)
from app.db.repositories.transaction import MoneyTransaction
from app.db.repositories.user import Users
from app.db.repositories.wallet import Wallet
from app.db.repositories.category import Category

# Helper file for alembic
# NOTE: Don't import from anywhere in application to this file directly
# to get tables use app.db.repositories.helpers.get_tables

__all__ = (
	'ProductSeller',
	'Reviews',
	'ProductLists',
	'ListsToProducts',
	'UserToGroups',
	'Permissions',
	'Users',
	'MoneyTransaction',
	'Seller',
	'Wallet',
	'Groups',
	'Comments',
	'Category',
	'Products',
	'ProductTags',
	'TextEntity',
	'TextEntityComment',
	'TextEntityProduct',
	'TextEntityUser',
	'TextEntityReview',
	'Tags',
)

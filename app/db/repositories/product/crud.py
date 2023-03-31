from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.product import ProductInCreate, ProductInUpdate
from ..comments import Comments
from ..common import BaseCrud
from .model import Products
from ..review import Reviews


class ProductsCRUD(BaseCrud[Products, ProductInCreate, ProductInUpdate]):
	model = Products

	@classmethod
	async def add_comments(
			cls,
			db: AsyncSession,
			product: Products,
			*comments: Comments
	) -> None:
		"""
		Comment does not intended to get by one,
		only when you have all products
		"""
		product.comments.extend(comments)
		db.add(product)
		await db.commit()

	@classmethod
	async def add_reviews(
			cls,
			db: AsyncSession,
			product: Products,
			*reviews: Reviews
	) -> None:
		"""
		Same as add_comment
		"""
		product.reviews.extend(reviews)
		db.add(product)
		await db.commit()

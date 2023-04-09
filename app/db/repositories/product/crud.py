from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.product import ProductInCreate, ProductInUpdate
from app.services.filler import fill
from app.services.text_entities import Parser
from ..comments import Comments
from ..common import BaseCrud
from .model import Products
from ..review import Reviews
from ..seller import ProductSeller
from ..text_entities import TextEntityProduct, TextEntitiesCRUD


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

	@classmethod
	async def create(cls, db: AsyncSession, obj_in: ProductInCreate) -> Products:
		parsed_entities = Parser().parse_entities(obj_in.description)
		parsed_entities = await TextEntitiesCRUD.create_list(db, parsed_entities, typ=TextEntityProduct)
		sellers = []
		for seller in obj_in.sellers:
			sellers.append(fill(seller, ProductSeller))
		relations = {"comments": [], "text_entities": parsed_entities, "sellers": sellers}
		product = await ProductsCRUD.create_with_relationship(db, obj_in, **relations)
		return product

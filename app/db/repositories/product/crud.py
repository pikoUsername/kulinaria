from typing import TYPE_CHECKING, List, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.schemas.category import CategoryInCreate
from app.models.schemas.product import ProductInCreate, ProductInUpdate
from app.models.schemas.seller import SellerInCreate
from app.models.schemas.tags import TagsInCreate
from app.services.filler import fill
from app.services.text_entities import Parser
from app.services.utils import generate_slug_for_category
from ..category import CategoryCRUD
from ..tags import Tags, ProductTags

if TYPE_CHECKING:
	from ..comments import Comments
	from ..review import Reviews
from ..common import BaseCrud
from .model import Products
from ..seller import ProductSeller, SellerCRUD
from ..text_entities import TextEntityProduct, TextEntitiesCRUD


class ProductsCRUD(BaseCrud[Products, ProductInCreate, ProductInUpdate]):
	model = Products

	@classmethod
	async def add_comments(
			cls,
			db: AsyncSession,
			product: Products,
			*comments: "Comments"
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
			*reviews: "Reviews"
	) -> None:
		"""
		Same as add_comment
		"""
		product.reviews.extend(reviews)
		db.add(product)
		await db.commit()

	@classmethod
	async def add_tags(cls, db: AsyncSession, tags: List[TagsInCreate], product: Products) -> None:
		result_tags = []
		for tag in tags:
			result_tags.append(fill(tag, ProductTags))
		product.tags = result_tags
		await db.flush([product])

	@classmethod
	async def create(cls, db: AsyncSession, obj_in: ProductInCreate) -> Products:
		parsed_entities = Parser().parse_entities(obj_in.description)
		parsed_entities = await TextEntitiesCRUD.create_list(db, parsed_entities, typ=TextEntityProduct)
		sellers = []
		for seller in obj_in.sellers:
			sellers.append(fill(seller, ProductSeller))
		tags = []

		category = CategoryInCreate(
			name=obj_in.category,
			slug=generate_slug_for_category(obj_in.category),
		)
		category, _ = await CategoryCRUD.get_or_create(db, category, id_name="name")

		relations = {"comments": [], "text_entities": parsed_entities, "sellers": sellers, "tags": tags, "category": category}
		logger.info(relations)

		product = await ProductsCRUD.create_with_relationship(db, obj_in, **relations)

		await cls.add_tags(db, obj_in.tags, product)
		return product

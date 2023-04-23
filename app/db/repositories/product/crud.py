from typing import TYPE_CHECKING, List, cast

from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.category import CategoryInCreate
from app.models.schemas.pagination import PaginationInfo
from app.models.schemas.product import ProductInCreate, ProductInUpdate
from app.models.schemas.search import SearchRequest
from app.models.schemas.tags import TagsInCreate
from app.services.filler import fill
from app.services.text_entities import Parser
from app.services.utils import generate_slug_for_category
from ..category import CategoryCRUD, Category
from ..tags import ProductTags
from ..common import BaseCrud
from .model import Products

if TYPE_CHECKING:
	from ..comments import Comments
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
		for tag in tags:
			product.tags.append(fill(tag, ProductTags))
		logger.info(f"Created tags: {product.tags}")
		db.add(product)
		await db.commit()
		await db.refresh(product)

	@classmethod
	async def create(cls, db: AsyncSession, obj_in: ProductInCreate) -> Products:
		parsed_entities = Parser().parse_entities(obj_in.description)
		parsed_entities = await TextEntitiesCRUD.create_list(db, parsed_entities, typ=TextEntityProduct)
		sellers = []
		for seller in obj_in.sellers:
			sellers.append(fill(seller, ProductSeller))
		tags = []
		for tag in obj_in.tags:
			tags.append(fill(tag, ProductTags))
		category = CategoryInCreate(
			name=obj_in.category,
			slug=generate_slug_for_category(obj_in.category),
		)
		category, _ = await CategoryCRUD.get_or_create(db, category, id_name="name")

		relations = {"comments": [], "text_entities": parsed_entities, "sellers": sellers, "tags": tags, "category": category}

		product = await ProductsCRUD.create_with_relationship(db, obj_in, **relations)

		return product

	@classmethod
	async def search(cls, db: AsyncSession, search_request: SearchRequest, pagination_info: PaginationInfo = None) -> List[Products]:
		request = []
		if search_request.request_str:
			request.append(
				Products.ts_vector.bool_op("@@")
				(func.to_tsquery(search_request.request_str))
			)
		if search_request.price_base and search_request.price_end:
			request.extend(
				(
					ProductSeller.product_id == Products.id,
					search_request.price_base <= ProductSeller.price,
					ProductSeller.price <= search_request.price_end,
				)
			)
		if search_request.category:
			request.extend(
				(
					Products.category_id == Category.id,
					Category.ts_vector.match(search_request.category),
				)
			)
		if search_request.rating:
			request.append(
				Products.rating >= search_request.rating,
			)
		if search_request.tags:
			request.extend(
				(
					ProductTags.product_id == Products.id,
					ProductTags.ts_vector.bool_op("@@")(" | ".join(search_request.tags))
				)
			)

		stmt = select(Products).distinct().where(
			*request
		).join(ProductSeller).join(Category).join(ProductTags).limit(
			pagination_info.for_page
		).offset(
			pagination_info.current_index * pagination_info.for_page
		)
		logger.info(stmt)

		results = await db.execute(stmt)
		results = results.scalars()
		return cast(List[Products], results.all())

	@classmethod
	async def random(cls, db: AsyncSession, limit: int, category: str = None) -> List[Products]:
		stmt = select(Products)
		if category:
			stmt = stmt.where(Category.name == category)
		stmt = stmt.order_by(func.random()).limit(limit)
		result = await db.execute(stmt)
		results = cast(List[Products], result.scalars().all())

		return results

from typing import List

from fastapi import APIRouter, Depends, Body, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_connection
from app.api.dependencies.permissions import CheckPermission
from app.db.repositories.comments import CommentsCRUD
from app.db.repositories.product import ProductsCRUD, Products
from app.api.dependencies.authentication import get_current_user_authorizer
from app.db.repositories.review import ReviewCrud
from app.db.repositories.user import Users
from app.models.domain import SellerInDB, TextEntitiesInDB
from app.models.domain.text_entities import TextEntityProductInDB
from app.models.schemas.base import BoolResponse
from app.models.schemas.comment import CommentInCreate, CommentInResponse
from app.models.schemas.product import ProductInResponse, ProductInCreate, ProductInUpdate
from app.models.schemas.product_seller import ProductSellerInResponse
from app.models.schemas.review import ReviewInCreate
from app.resources import strings
from app.services.utils import convert_db_obj_to_model, convert_list_obj_to_model


router = APIRouter(tags=["product"])


@router.post(
	"/",
	name="products:create-product",
	dependencies=[Depends(CheckPermission("*", Products))]
)
async def create_product(
		product_create: ProductInCreate = Body(..., embed=True, alias="product"),
		db: AsyncSession = Depends(get_connection),
) -> ProductInResponse:
	if product := await ProductsCRUD.get_by_kwargs(db, slug=product_create.slug):
		raise HTTPException(
			detail=strings.DUPLICATE_ERROR.format(
				model=Products.__tablename__,
				id=product.id
			),
			status_code=400,
		)
	product = await ProductsCRUD.create(db, obj_in=product_create)

	return ProductInResponse(
		name=product.name,
		description=product.description,
		sellers=product_create.sellers,
		text_entities=convert_list_obj_to_model(product.text_entities, TextEntityProductInDB),
	)


@router.get(
	"/{product_id}",
	name="products:get-product",
)
async def get_product(
		product_id: int,
		db: AsyncSession = Depends(get_connection)
) -> ProductInResponse:
	product = await ProductsCRUD.get(db, product_id)
	if not product:
		raise HTTPException(
			detail=strings.DOES_NOT_EXISTS.format(model=Products.__tablename__, id=product_id),
			status_code=400,
		)

	return ProductInResponse(
		name=product.name,
		description=product.description,
		seller=convert_db_obj_to_model(product.seller, SellerInDB),
		text_entities=product.text_entities,
	)


@router.put(
	"/{product_id}",
	name="products:update-product",
	dependencies=[Depends(CheckPermission("update", Products))]
)
async def update_product(
	product_id: int,
	product_body: ProductInUpdate = Body(..., embed=True, alias="product"),
	db: AsyncSession = Depends(get_connection)
) -> ProductInResponse:
	product = await ProductsCRUD.get(db, product_id)
	if not product:
		raise HTTPException(
			detail=strings.DOES_NOT_EXISTS.format(model=Products.__tablename__),
			status_code=400,
		)

	product = await ProductsCRUD.update(db, product, product_body)

	return ProductInResponse(
		name=product.name,
		description=product.description,
		seller=convert_db_obj_to_model(product.seller, SellerInDB),
		text_entities=product.text_entities
	)


@router.delete(
	"/{product_id}",
	name="products:delete-product",
	dependencies=[Depends(CheckPermission("delete", Products))]
)
async def delete_product(
		product_id: int,
		db: AsyncSession = Depends(get_connection),
) -> ProductInResponse:
	if not await ProductsCRUD.get(db, product_id):
		raise HTTPException(
			detail=strings.DOES_NOT_EXISTS.format(
				model=Products.__tablename__,
				id=product_id
			),
			status_code=400,
		)
	deleted_product = await ProductsCRUD.delete(db, product_id)
	logger.info("Product deleted", extra={"product": deleted_product})

	return ProductInResponse(
		name=deleted_product.name,
		description=deleted_product.description,
		seller=convert_db_obj_to_model(deleted_product.seller, SellerInDB),
		text_entities=convert_list_obj_to_model(deleted_product.text_entities, TextEntitiesInDB),
	)


@router.post(
	"/{product_id}/review",
	name="products:review",
)
async def review_product(
		product_id: int,
		review: ReviewInCreate = Body(..., embed=True),
		db: AsyncSession = Depends(get_connection),
		user: Users = Depends(
			get_current_user_authorizer(required=True)),  # this way you don't let anonymous users left reviews
) -> BoolResponse:
	product = await ProductsCRUD.get(db, product_id)

	if not product:
		raise HTTPException(
			detail=strings.DOES_NOT_EXISTS.format(
				model=Products.__tablename__,
				id=product_id
			),
			status_code=400,
		)

	review = await ReviewCrud.create(db, review)
	await ProductsCRUD.add_reviews(db, product, review)

	return BoolResponse(
		ok=True,
	)


@router.post(
	"/{product_id}/comment",
	name="products:comment",
)
async def add_comment(
		product_id: int,
		comment: CommentInCreate = Body(..., embed=True),
		db: AsyncSession = Depends(get_connection),
		user: Users = Depends(
			get_current_user_authorizer(required=True)),  # this way you don't let anonymous users left comments
) -> BoolResponse:
	product = await ProductsCRUD.get(db, product_id)

	if not product:
		raise HTTPException(
			detail=strings.DOES_NOT_EXISTS.format(
				model=Products.__tablename__,
				id=product_id
			),
			status_code=400,
		)

	comment = await CommentsCRUD.create(db, comment)
	await ProductsCRUD.add_comments(db, product, comment)

	return BoolResponse(
		ok=True,
	)


@router.get(
	"/{product_id}/comments",
	name="products:get-comments",
)
async def get_comments(
		product_id: int,
		db: AsyncSession = Depends(get_connection),
) -> List[CommentInResponse]:
	product = await ProductsCRUD.get(db, product_id)

	if not product:
		raise HTTPException(
			detail=strings.DOES_NOT_EXISTS.format(
				model=Products.__tablename__,
				id=product_id
			),
			status_code=400,
		)

	comments = convert_list_obj_to_model(product.comments, CommentInResponse)

	return comments


@router.get(
	"/{product_id}/sellers",
	name="products:get-sellers",
)
async def get_sellers(
		product_id: int,
		db: AsyncSession = Depends(get_connection),
) -> List[ProductSellerInResponse]:  # TODO
	product = await ProductsCRUD.get(db, product_id)

	if not product:
		raise HTTPException(
			detail=strings.DOES_NOT_EXISTS.format(
				model=Products.__tablename__,
				id=product_id
			),
			status_code=400,
		)
	sellers = product.sellers
	return convert_list_obj_to_model(sellers, ProductSellerInResponse)


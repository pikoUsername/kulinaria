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
from app.db.repositories.seller import ProductSeller
from app.db.repositories.user import Users, UserCrud
from app.models.domain import SellerInDB, TextEntitiesInDB, ProductInDB, ProductSellerInDB
from app.models.domain.text_entities import TextEntityProductInDB
from app.models.schemas.base import BoolResponse
from app.models.schemas.cart import CartListInResponse
from app.models.schemas.comment import CommentInCreate, CommentInResponse
from app.models.schemas.product import ProductInResponse, ProductInCreate, ProductInUpdate
from app.models.schemas.product_seller import ProductSellerInResponse
from app.models.schemas.review import ReviewInCreate
from app.resources import strings
from app.services.utils import convert_db_obj_to_model, convert_list_obj_to_model


router = APIRouter(tags=["product"])


@router.get(
	'/get_cart',
	name="product:get_cart",
)
async def get_cart(
	user: Users = Depends(get_current_user_authorizer(required=True)),
	db: AsyncSession = Depends(get_connection),
) -> CartListInResponse:
	products = await UserCrud.get_cart(db, user)
	result_products = convert_list_obj_to_model(products, ProductInResponse)
	return CartListInResponse(
		products=result_products,
	)


@router.post(
	"/",
	name="product:create-product",
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

	sellers = []

	for seller in product.sellers:
		seller: ProductSeller
		logger.info(seller.seller.__dict__)
		sellers.append(
			ProductSellerInDB(
				id=seller.id,
				description=seller.description,
				seller=seller.seller,
				name=seller.name,
				where=seller.wher,
				where_name=seller.where_name,
				price=seller.price,
				link=seller.link
			)
		)

	return ProductInResponse(
		slug=product.slug,
		name=product.name,
		rating=product.rating,
		description=product.description,
		sellers=convert_list_obj_to_model(product.sellers, ProductSellerInDB),
		text_entities=convert_list_obj_to_model(product.text_entities, TextEntityProductInDB),
	)


@router.get(
	"/{product_id}",
	name="product:get-product",
)
async def get_product(
		product_id: int,
		db: AsyncSession = Depends(get_connection)
) -> ProductInResponse:
	product = await ProductsCRUD.get_by_kwargs(db, id=product_id)
	if not product:
		raise HTTPException(
			detail=strings.DOES_NOT_EXISTS.format(model=Products.__tablename__, id=product_id),
			status_code=400,
		)

	return ProductInResponse(
		slug=product.slug,
		name=product.name,
		description=product.description,
		sellers=convert_list_obj_to_model(product.sellers, ProductSellerInDB),
		text_entities=product.text_entities,
	)


@router.put(
	"/{product_id}",
	name="product:update-product",
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
			detail=strings.DOES_NOT_EXISTS.format(model=Products.__tablename__, id=product_id),
			status_code=400,
		)

	product = await ProductsCRUD.update(db, product, product_body)

	return ProductInResponse(
		slug=product.slug,
		name=product.name,
		description=product.description,
		seller=convert_db_obj_to_model(product.seller, SellerInDB),
		text_entities=product.text_entities
	)


@router.delete(
	"/{product_id}",
	name="product:delete-product",
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
		slug=deleted_product.slug,
		name=deleted_product.name,
		description=deleted_product.description,
		seller=convert_db_obj_to_model(deleted_product.seller, SellerInDB),
		text_entities=convert_list_obj_to_model(deleted_product.text_entities, TextEntitiesInDB),
	)


@router.post(
	"/{product_id}/review",
	name="product:review",
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
	name="product:comment",
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
	name="product:get-comments",
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
	name="product:get-sellers",
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


@router.post(
	"/{product_id}/add_cart",
	name="product:add_cart",
)
async def add_favourite(
		product_id: int,
		user: Users = Depends(get_current_user_authorizer(required=True)),
		db: AsyncSession = Depends(get_connection),
) -> BoolResponse:
	product = await ProductsCRUD.get(db, id=product_id)
	if not product:
		raise HTTPException(
			detail=strings.DOES_NOT_EXISTS.format(
				model=Products.__tablename__,
				id=product_id
			),
			status_code=400,
		)
	await UserCrud.add_product_cart(db, user, product)
	return BoolResponse(ok=True)


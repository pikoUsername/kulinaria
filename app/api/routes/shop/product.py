from fastapi import APIRouter, Depends, Body, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_connection
from app.api.dependencies.permissions import CheckPermission
from app.db.repositories.product import ProductsCRUD, Products
from app.db.repositories.seller import SellerCRUD
from app.models.domain import SellerInDB, TextEntitiesInDB
from app.models.schemas.base import BoolResponse
from app.models.schemas.product import ProductInResponse, ProductInCreate, ProductInUpdate
from app.services.text_entities import Parser
from app.db.repositories.text_entities import TextEntitiesCRUD
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
	seller = await SellerCRUD.get_by_kwargs(
		db, id=product_create.seller_id
	)
	if product := await ProductsCRUD.get_by_kwargs(db, seller_id=seller.id, name=product_create.name):
		raise HTTPException(
			detail=strings.DUPLICATE_ERROR.format(
				model=Products.__tablename__,
				id=product.id
			),
			status_code=400,
		)
	parsed_entities = Parser().parse_entities(product_create.description)
	parsed_entities = await TextEntitiesCRUD.create_list(db, parsed_entities)
	relations = {"seller": seller, "comments": [], "text_entities": parsed_entities}
	product = await ProductsCRUD.create_with_relationship(db, product_create, **relations)
	return ProductInResponse(
		name=product.name,
		description=product.description,
		seller=convert_db_obj_to_model(seller, SellerInDB),
		text_entities=parsed_entities,
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
	"/{product_id}/rate",
	name="products:rate",
	dependencies=[],
)
async def rate(
		product_id: int,
		db: AsyncSession = Depends(get_connection),
) -> BoolResponse:
	product = await ProductsCRUD.get(db, product_id)


	await ProductsCRUD.update(
		db,

	)

	return BoolResponse(
		ok=True,
	)

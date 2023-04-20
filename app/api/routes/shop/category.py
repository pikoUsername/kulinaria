from typing import List

from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_connection
from app.models.domain import ProductInDB, CategoryInDB
from app.models.schemas.category import PaginatedCategoryListResponse
from app.models.schemas.pagination import PaginationInfo
from app.db.repositories.category import CategoryCRUD, Category
from app.models.schemas.product import ProductListsInResponse
from app.services.utils import convert_list_obj_to_model
from app.resources import strings


router = APIRouter(tags=["category"])


@router.get("/all", name="category:get-all-categories")
async def get_all_categories(
        limit: int = Query(default=None),
        db: AsyncSession = Depends(get_connection),
) -> List[CategoryInDB]:
    categories = await CategoryCRUD.get_multi(db, limit)
    return convert_list_obj_to_model(categories, CategoryInDB)


@router.get("/{name}/all", name="category:get-category-products")
async def get_category_products(
        name: str,
        db: AsyncSession = Depends(get_connection),
) -> ProductListsInResponse:
    """
    Not recomended, it will overload uvicorn server
    """
    # yeah, broken DRY
    category = await CategoryCRUD.get_by_kwargs(db, name=name)
    if not category:
        raise HTTPException(
            detail=strings.DOES_NOT_EXISTS.format(
                model=Category.__tablename__,
                id=name,
            ),
            status_code=400,
        )
    products = await CategoryCRUD.get_products_all(db, category)
    return ProductListsInResponse(
        products=convert_list_obj_to_model(products, ProductInDB),
        size=len(products),
    )


@router.post("/{name}/all_paginated", name="category:get-category-products")
async def get_category_products(
        name: str,
        pagination_info: PaginationInfo = Body(..., embed=True, alias="pagination"),
        db: AsyncSession = Depends(get_connection),
) -> PaginatedCategoryListResponse:
    category = await CategoryCRUD.get_by_kwargs(db, name=name)
    if not category:
        raise HTTPException(
            detail=strings.DOES_NOT_EXISTS.format(
                model=Category.__tablename__,
                id=name,
            ),
            status_code=400,
        )
    products = await CategoryCRUD.get_paginated_products(db, pagination_info, category=category)
    if not products:
        raise HTTPException(
            detail=strings.DOES_NOT_EXISTS.format(
                model=Category.__tablename__,
                id=name,
            ),
            status_code=400,
        )
    page_count = await CategoryCRUD.get_total_pages_of_products(db, pagination_info, category=category)
    return PaginatedCategoryListResponse(
        page_count=page_count,
        for_page=pagination_info.for_page,
        result_len=len(products),
        products=convert_list_obj_to_model(products, ProductInDB),
    )


@router.get("/{name}/random")
async def get_random_products(
        name: str,
        limit: int = Query(default=10),
        db: AsyncSession = Depends(get_connection)
) -> ProductListsInResponse:
    category = await CategoryCRUD.get_by_kwargs(db)
    if not category:
        raise HTTPException(
            detail=strings.DOES_NOT_EXISTS.format(
                model=Category.__tablename__,
                id=name,
            ),
            status_code=400,
        )

    products = await CategoryCRUD.get_random_products(db, category, limit=limit)

    return ProductListsInResponse(
        products=products,
        size=len(products),
    )

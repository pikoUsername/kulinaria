from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_connection
from app.models.domain import ProductInDB
from app.models.schemas.category import PaginatedCategoryListResponse
from app.models.schemas.pagination import PaginationInfo
from app.db.repositories.category import CategoryCRUD, Category
from app.models.schemas.search import SearchRequest
from app.services.utils import convert_list_obj_to_model
from app.resources import strings

router = APIRouter(tags=["category"])


@router.post("/{category_id}/all", name="category:get-category-products")
async def get_category_products(
        category_id: int,
        pagination_info: PaginationInfo = Body(..., embed=True, alias="pagination"),
        db: AsyncSession = Depends(get_connection),
) -> PaginatedCategoryListResponse:
    category = await CategoryCRUD.get(db, id=category_id)
    if not category:
        raise HTTPException(
            detail=strings.DOES_NOT_EXISTS.format(
                model=Category.__tablename__,
                id=category_id,
            ),
            status_code=400,
        )
    products = await CategoryCRUD.get_paginated_products(db, pagination_info, category_id=category_id)
    page_count = await CategoryCRUD.get_total_pages_of_products(db, pagination_info, category_id=category_id)
    return PaginatedCategoryListResponse(
        page_count=page_count,
        for_page=pagination_info.for_page,
        result_len=len(products),
        products=convert_list_obj_to_model(products, ProductInDB),
    )


@router.post("/{category_id}/search", name="category:search-by-category")
async def category_search(
        category_id: int,
        search_request: SearchRequest = Body(..., alias="search", embed=True),
        pagination_info: PaginationInfo = Body(..., alias="pagination", embed=True),
        db: AsyncSession = Depends(get_connection),
) -> PaginatedCategoryListResponse:
    pass

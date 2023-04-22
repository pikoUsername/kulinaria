from fastapi import APIRouter, Depends, Body, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_connection
from app.db.repositories.product import ProductsCRUD
from app.models.domain import ProductInDB
from app.models.schemas.pagination import PaginationInfo
from app.models.schemas.product import ProductListsInResponse
from app.models.schemas.search import SearchRequest
from app.services.utils import convert_list_obj_to_model

router = APIRouter(tags=["search"])


@router.post("/", name="search:search_products")
async def search_products(
        search_request: SearchRequest = Body(..., embed=True, alias="search"),
        pagination_info: PaginationInfo = Body(..., alias="pagination", embed=True),
        db: AsyncSession = Depends(get_connection),
) -> ProductListsInResponse:
    """
    Attempt to use search engines, particulary ElasticSearch
    """
    results = await ProductsCRUD.search(db, search_request, pagination_info)
    return ProductListsInResponse(
        products=convert_list_obj_to_model(results, ProductInDB),
        size=len(results),
    )


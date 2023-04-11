from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_connection
from app.models.schemas.search import SearchRequest

router = APIRouter(tags=["search"])


@router.post("/", name="search:search_product")
async def search_product(
        search_request: SearchRequest = Body(..., embed=True, alias="search"),
        db: AsyncSession = Depends(get_connection),
):
    pass

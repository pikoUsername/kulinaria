from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_connection
from app.models.schemas.base import BoolResponse

router = APIRouter()


@router.get("/alive")
async def alive(db: AsyncSession = Depends(get_connection)) -> BoolResponse:
    # there had to be checks for ElasticSearch, postgres, and redis,
    # but there will be only for postgres
    await db.execute(select(func.current_timestamp))
    return BoolResponse(ok=True)

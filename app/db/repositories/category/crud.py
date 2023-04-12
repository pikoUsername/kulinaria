from typing import List, TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain.category import CategoryInDB
from app.models.schemas.category import CategoryInCreate
from app.models.schemas.pagination import PaginationInfo
from ..common import BaseCrud
from .model import Category

if TYPE_CHECKING:
    from ..product import Products


class CategoryCRUD(BaseCrud[Category, CategoryInCreate, CategoryInDB]):
    model = Category

    @classmethod
    async def get_paginated_products(
            cls,
            db: AsyncSession,
            pag_info: PaginationInfo,
            category_id: int
    ) -> List["Products"]:
        pass

    @classmethod
    async def get_total_pages_of_products(
            cls,
            db: AsyncSession,
            pagination_info: PaginationInfo,
            category_id: int,
    ) -> int:
        pass

    @classmethod
    async def create(cls, db: AsyncSession, obj_in: CategoryInCreate) -> Category:
        obj_in.slug = obj_in.name
        return await super().create(db, obj_in)

from typing import List, cast, TYPE_CHECKING

from sqlalchemy import select, func
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
    async def get_products_all(
            cls,
            db: AsyncSession,
            category: Category,
    ) -> List["Products"]:
        from ..product import Products

        # dont fetch this way, it will overload server
        stmt = select(Products).where(
            Products.category_id == category.id,
        )
        result = await db.scalars(stmt)
        return cast(List["Products"], result.all())

    @classmethod
    async def get_paginated_products(
            cls,
            db: AsyncSession,
            pag_info: PaginationInfo,
            category: Category,
    ) -> List["Products"]:
        from ..product import Products

        stmt = select(Products).where(
            Products.category_id == category.id
        ).limit(
            pag_info.for_page
        ).offset(
            pag_info.for_page * pag_info.current_index
        )
        result = await db.execute(stmt)
        result = result.all()
        return cast(List["Products"], result)

    @classmethod
    async def get_total_pages_of_products(
            cls,
            db: AsyncSession,
            pagination_info: PaginationInfo,
            category: Category,
    ) -> int:
        from ..product import Products

        # i will fetch all products where category id is identical, and count them
        # this way it will be way more effective
        stmt = select(func.count()).select_from(
            Products
        ).where(
            Products.category_id == category.id
        )
        result = await db.execute(stmt)
        result = result.first()
        count = int(result[0])
               # 100    # 5
        return count // pagination_info.for_page

    @classmethod
    async def create(cls, db: AsyncSession, obj_in: CategoryInCreate) -> Category:
        obj_in.slug = obj_in.name
        return await super().create(db, obj_in)

    @classmethod
    async def get_random_products(cls, db: AsyncSession, category: Category, limit: int) -> List["Products"]:
        from ..product import Products

        stmt = select(
            Products
        ).where(
            Products.category_id == category.id
        ).order_by(
            func.random
        ).limit(limit)

        results = await db.scalars(stmt)
        results = results.all()
        return cast(List["Products"], results)

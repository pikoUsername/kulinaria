from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import ProductListInDB
from ..common import BaseCrud

from .model import ProductLists
from ..product import Products


class ProductListCrud(BaseCrud[ProductLists, ProductListInDB, ProductListInDB]):
	model = ProductLists

	async def add_products(
			self,
			db: AsyncSession,
			product_list: ProductLists,
			*products: Products,
	) -> None:
		product_list.products.extend(products)
		db.add(product_list)
		await db.commit()

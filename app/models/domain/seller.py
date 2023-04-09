from __future__ import annotations
from typing import List, TYPE_CHECKING, Tuple, Optional

from pydantic import Field

from .rwmodel import RWModel
from ..common import DateTimeModelMixin, IDModelMixin

if TYPE_CHECKING:
	from .products import ProductInDB


class ProductSellerInDB(RWModel, IDModelMixin, DateTimeModelMixin):
	product: ProductInDB
	seller: SellerInDB
	description: str
	name: str = Field(..., max_length=52)
	where: Optional[Tuple[float, float]] = None
	where_name: str = Field(..., max_length=100)
	price: int
	link: str


class SellerInDB(RWModel, IDModelMixin, DateTimeModelMixin):
	rating: int = Field(None)
	product_seller: List[ProductSellerInDB] = []
	country: str
	is_activated: bool = Field(default=True)
	is_blocked: bool = Field(default=False)

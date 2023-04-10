from typing import List, Optional

from pydantic import BaseModel


class SellerData(BaseModel):
    name: str
    link: str
    description: str
    price: int
    color: Optional[str] = None
    img_url: str


class ProductData(BaseModel):
    # СДЕЛАТЬ что бы не зависил от порядка вкладывания
    name: str
    category: str
    short_description: Optional[str] = ""
    characteristics: str  # они могут быть ОЧЕНЬ разными!  разделитель \n
    tags: List[str]
    sellers: List[SellerData]

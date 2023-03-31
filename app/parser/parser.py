import asyncio
from asyncio import AbstractEventLoop
from typing import Optional, List

from pydantic import BaseModel

from app.core.config import get_app_settings
from app.core.settings.app import AppSettings


class EKatalogTag(BaseModel):
    name: str


class SellerLink(BaseModel):
    name: str
    link: str
    description: str
    price: int
    color: str


class ProductData(BaseModel):
    name: str
    category: str
    short_description: str
    tags: Optional[str]
    sellers: List[SellerLink]


class ParserRunner:
    def __init__(self, settings: AppSettings, loop: Optional[AbstractEventLoop] = None):
        self.settings = settings
        self.loop = loop
        self.session = None

    def configure(self):
        pass

    async def run(self) -> None:
        while 1:
            pass

    def extract_info_from_page(self, url: str) -> ProductData:
        pass

    def get_product_links(self, url: str) -> List[str]:
        pass

def run_parser():
    """
    Раннится с помощью крона в ночь
    Потом выгружает в ночь в csv формат.
    Парсит данные об продуктах на платформе e-katalog
    и сразу же загружает эти данные в базу данных
    Это реализация будет использвать asyncio

    вопрос: как будет ранится бд?
    как будет организовано взаимодействие с бд?
    будет ли переиспользваны друие модули?

    1, 2) С помощью моделей в бд, как обычно
    создается мета и тд и тп. да, тоесть будет
    две сессии которые будут записывать в одну бд
    3) будут использваны модули core, и db.
    """
    settings = get_app_settings()
    runner = ParserRunner(settings)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.run)

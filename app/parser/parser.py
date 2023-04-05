import asyncio
from asyncio import AbstractEventLoop
from typing import Optional, List, Dict
import csv

from aiohttp import ClientSession

from bs4 import BeautifulSoup
from pydantic import BaseModel

from app.core.config import get_app_settings
from app.core.settings.app import AppSettings


TEST_PARSING_URLS = {
    "phone": "https://kz.e-katalog.com/list/122/",
    "memory card": "https://kz.e-katalog.com/list/32/",
    "tablets": "https://kz.e-katalog.com/list/30/",
}

SEPARATOR = '\n'


class SellerData(BaseModel):
    name: str
    link: str
    description: str
    price: int
    color: str


class ProductData(BaseModel):
    # СДЕЛАТЬ что бы не зависил от порядка вкладывания
    name: str
    category: str
    short_description: str
    characteristics: str  # они могут быть ОЧЕНЬ разными!  разделитель \n
    tags: Optional[str]
    sellers: List[SellerData]


class Parser:
    def __init__(
            self,
            settings: AppSettings,
            file: str,
            loop: Optional[AbstractEventLoop] = None,
            urls: Dict[str, str] = None,
    ) -> None:
        if urls is None:
            urls = TEST_PARSING_URLS
        self.settings = settings
        self.loop = loop
        self.urls = urls
        self.file = file

        self._current_url = ""

        self.client = ClientSession(loop=loop)

    async def get_data(self, urls: List[str] = None) -> List[ProductData]:
        """
        Короче сваливается ВСЕ в одну свалку и кидается потом на CSV
        """
        if urls is None:
            urls = self.urls
        # сперва собирается ссылки на товары!
        # потом после сборов открываются все эти товары
        # и отправляются в csv
        result = []

        # надо попробывать ввести limit
        # настраевыемость, читабельность, и разделение на этапы
        # так как такой код никуда не пойдет
        for url in urls:
            if not url.endswith("/"):
                url += "/"
            # это первая страница
            content = await (await self.client.get(url)).text()
            count = self.extract_pages_count(content)
            for i in range(count):
                content = await (await self.client.get(url + f"{i}/")).text()
                # она будет заниматся и переходом на другие страницы
                urls = self.get_product_links(content)
                result_list = []
                # боже, тройной for!
                for sub_url in urls:
                    content = await (await self.client.get(sub_url)).text()
                    result_ = await self.extract_detailed_info_from_page(content)
                    result_list.append(result_)
                result.extend(result_list)

        return result

    def write_data(self, data: List[ProductData]) -> None:
        row_meta = ProductData.__fields__.keys()
        with open(self.file, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row_meta)
            for value in data:
                # нужно тестирование
                writer.writerow(value)

    def extract_pages_count(self, content: str) -> int:
        # короче у них ебнутая система
        # их юрл типо https://kz.e-katalog.com/list/30 первая страница
        # начинается с /0 и потом 3 это /2. Идиотия(((
        parser = BeautifulSoup(content, "html.parser")

        result = parser.select("ib page-num > ib")
        result = len(result)

        return result

    async def extract_detailed_info_from_page(self, content: str) -> ProductData:
        parser = BeautifulSoup(content, "html.parser")

        # sub_type_ = parser.find(class_="t2 no-mobile ib h1")
        name = parser.find('h1', iterprop="name", class_="t2 no-mobile ib").get_text()
        full_desc = parser.find(class_='desc-ai-title', iterprop='description')
        short_desc = full_desc.find_all("p")[0].get_text()
        short_desc_first_letter = full_desc.find("span", class_="desc-ai-initcap").get_text()
        short_desc = short_desc_first_letter + short_desc

        tags_div = parser.find("div", class_="m-c-f1")
        tags_raw = tags_div.find_all("a", class_="ib no-u")
        tags = []
        for tag in tags_raw:
            tags.append(tag.get_text())

        charc_raw = parser.find("div", class_="m-c-f2")
        charc_list = []
        for charc in charc_raw.find_all("div"):
            charc.append(charc['title'])
        characteristics = SEPARATOR.join(charc_list)
        url_seller = parser.find("desc-menu").find_all("a")[0]
        url_seller = url_seller['href']

        prices = await (await self.client.get(url_seller)).text()

        sellers = self.get_sellers(prices)

        catalog_path = parser.find("div", class_="catalog-path s-width").find_all("a")
        category = catalog_path[-2]

        return ProductData(
            name=name,
            category=category,
            short_description=short_desc,
            characteristics=characteristics,
            tags=tags,
            sellers=sellers,
        )

    def get_sellers(self, content: str) -> List[SellerData]:
        pass

    def get_product_links(self, content: str) -> List[str]:
        parser = BeautifulSoup(content, "html.parser")
        products = parser.find('form', id='list_form1').select('div[id]')
        for product in products:
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
    runner = Parser(settings, "./assets/db.csv", urls=TEST_PARSING_URLS)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.run())

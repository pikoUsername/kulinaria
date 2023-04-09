import asyncio
from asyncio import AbstractEventLoop
from typing import Optional, List, Dict
import csv

from aiohttp import ClientSession
from loguru import logger

from bs4 import BeautifulSoup
from pydantic import BaseModel


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
    color: Optional[str] = None
    img_url: str


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
            file: str,
            loop: Optional[AbstractEventLoop] = None,
            urls: Dict[str, str] = None,
    ) -> None:
        if urls is None:
            urls = TEST_PARSING_URLS
        self.loop = loop
        self.urls = urls
        self.file = file

        self._current_url = ""

        self.client = ClientSession(loop=loop)

        self.parent_url = "https://kz.e-katalog.com/"

    async def get_data(self, urls: List[str] = None) -> List[ProductData]:
        """
        Короче сваливается ВСЕ в одну свалку и кидается потом на CSV
        """
        if urls is None:
            urls = self.urls
        logger.info(f"Urls: {urls}")
        # сперва собирается ссылки на товары!
        # потом после сборов открываются все эти товары
        # и отправляются в csv
        result = []

        # надо попробывать ввести limit
        # настраевыемость, читабельность, и разделение на этапы
        # так как такой код никуда не пойдет
        for url in urls.values():
            if not url.endswith("/"):
                url += "/"
            # это первая страница
            content = await (await self.client.get(url)).text()
            count = self.extract_pages_count(content)
            logger.info(f"Pages count: {count}")
            for i in range(count):
                content = await (await self.client.get(url + f"{i}/")).text()
                # она будет заниматся и переходом на другие страницы
                urls = self.get_product_links(content)
                result_list = []
                # боже, тройной for!
                for sub_url in urls:
                    logger.info(f"Parsing data url of: {sub_url}")
                    content = await (await self.client.get(self.parent_url + sub_url)).text()
                    result_ = await self.extract_detailed_info_from_page(content)
                    result_list.append(result_)
                result.extend(result_list)

        return result

    def write_file(self, data: List[ProductData], file: Optional[str] = None) -> None:
        if file is None:
            file = self.file
        row_meta = ProductData.__fields__.keys()
        with open(file, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row_meta)
            for value in data:
                # нужно тестирование
                writer.writerow(value.dict().values())

    def extract_pages_count(self, content: str) -> int:
        # короче у них ебнутая система
        # их юрл типо https://kz.e-katalog.com/list/30 первая страница
        # начинается с /0 и потом 3 это /2. Идиотия(((
        parser = BeautifulSoup(content, "html.parser")

        result = parser.find(class_="ib page-num")
        result = result.find_all("a")

        result = len(result)

        return result

    async def extract_detailed_info_from_page(self, content: str) -> ProductData:
        parser = BeautifulSoup(content, "html.parser")

        # sub_type_ = parser.find(class_="t2 no-mobile ib h1")
        name = parser.find('h1', itemprop="name")
        name = name.get_text()
        logger.info(f"Product name: {name}")
        full_desc = parser.find(class_='desc-ai-title', itemprop='description')
        short_desc = None
        if full_desc:
            if full_desc:
                logger.info(full_desc)
                short_desc = full_desc.find_all("p")[0].get_text()
            short_desc_first_letter = full_desc.find("span", class_="desc-ai-initcap")
            if short_desc_first_letter:
                short_desc_first_letter = short_desc_first_letter.get_text()
            if short_desc and short_desc_first_letter:
                short_desc = short_desc_first_letter + short_desc

        tags_div = parser.find("div", class_="m-c-f1")
        tags_raw = tags_div.find_all("a", class_="ib no-u")
        tags = []
        for tag in tags_raw:
            tags.append(tag.get_text())

        charc_raw = parser.find("div", class_="m-c-f2")
        charc_list = []
        for charc in charc_raw.find_all("div"):
            title = charc.get('title')
            if title:
                charc.append(title)
        characteristics = SEPARATOR.join(charc_list)
        url_seller = parser.find(class_="desc-menu").find_all("a")[0]
        url_seller = url_seller['link']

        prices = await (await self.client.get(self.parent_url + url_seller)).text()

        sellers = self.get_sellers(prices)

        catalog_path = parser.find("div", class_="catalog-path s-width").find_all("a")
        category = catalog_path[-2].get_text()

        return ProductData(
            name=name,
            category=category,
            short_description=short_desc or None ,
            characteristics=characteristics,
            tags=tags,
            sellers=sellers,
        )

    def get_sellers(self, content: str) -> List[SellerData]:
        parser = BeautifulSoup(content, "html.parser")

        seller_table = parser.find('table', class_="where-buy-table").find("tbody")
        sellers = seller_table.select('tr[class]')
        result = []
        for seller in sellers:
            name = seller.find(class_='where-buy-description').find('h3').get_text()
            price_td = seller.find(class_='where-buy-price')
            link = price_td.a['href']
            price = price_td.get_text().replace(' ', '')
            img = seller.find(class_='where-buy-img').find(class_='hide-blacked').find('img')['src']
            color_elem = seller_table.find(class_='where-buy-color')
            color = None
            if color_elem:
                bg_color = color_elem.find('div')['style']
                color = self.get_color_from_style_string(bg_color)

            desc = seller.find(class_='where-buy-description').find('it-desc').get_text()

            sell = SellerData(
                name=name,
                link=link,
                price=price,
                img_url=img,
                color=color,
                description=desc
            )
            result.append(sell)
        return result

    def get_color_from_style_string(self, color: str) -> str:
        """Format: background-color: #ffffff"""
        styles = color.split('\n')
        for style in styles:
            if 'background-color' in style:
                _, color = style.split(":")
                return color

    def get_product_links(self, content: str) -> List[str]:
        parser = BeautifulSoup(content, "html.parser")
        products = parser.find('form', id='list_form1').select('div[id]')
        links = []
        for product in products:
            # да
            link = product.find(class_="model-short-title")
            if not link:
                # it selects a div class with and without id
                continue
            link = link.get('href')
            links.append(link)
        return links

    async def close(self) -> None:
        await self.client.close()


class ParserRunner:
    def __init__(self, parser: Parser, settings) -> None:
        self.parser = parser

    async def run(self):
        pass


def parse_data(urls: Dict[str, str], file: str) -> None:
    """
    Парсится дата с е-каталога
    """
    loop = asyncio.get_event_loop()

    parser = Parser(file, urls=urls)
    try:
        data = loop.run_until_complete(parser.get_data())
        logger.info(f"Parser data: {data}")
        parser.write_file(data)
        logger.info("Parser has written data")
    except Exception:
        raise
    finally:
        loop.run_until_complete(parser.close())


def run_parser(file: str):
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
    from app.core.settings import get_app_settings

    parser = Parser(file, urls=TEST_PARSING_URLS)

    runner = ParserRunner(parser, get_app_settings())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.run())

import re
import asyncio
from asyncio import AbstractEventLoop
from typing import Optional, List, Dict, Set
import csv

from aiohttp import ClientSession
from loguru import logger
from bs4 import BeautifulSoup

from .schema import SellerData, ProductData
from .consts import TEST_PARSING_URLS, SEPARATOR, VALUE_SEP, URL_REGEX
from .utils import avg_rating


class Parser:
    """
    Предупреждение ГОВНОКОД
    """
    def __init__(
            self,
            file: str,
            loop: Optional[AbstractEventLoop] = None,
            urls: Dict[str, str] = None,
            limit: int = 4,
    ) -> None:
        if urls is None:
            urls = TEST_PARSING_URLS
        self.loop = loop
        self.urls = urls
        self.file = file
        self.limit = limit

        self._current_url = ""

        self.client = ClientSession(loop=loop)

        self.parent_url = "https://kz.e-katalog.com"

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
            j = 0
            logger.info(f"Pages count: {count}")
            for i in range(count):
                if j > self.limit:
                    logger.info("Reached limit for base url!!")
                    break
                content_category = await (await self.client.get(url + f"{i}/")).text()
                # она будет заниматся и переходом на другие страницы
                urls = self.get_product_links(content_category)
                result_list = []
                # боже, тройной for!
                for sub_url in urls:
                    if j > self.limit:
                        logger.info("Reached limit for base url!!")
                        break
                    logger.info(f"Parsing data url of: {sub_url}")
                    content = await (await self.client.get(self.parent_url + sub_url)).text()
                    rating = self.extract_rating_from_short_info(content_category, sub_url)
                    result_ = await self.extract_detailed_info_from_page(content, sub_url, rating)
                    result_list.append(result_)
                    j += 1
                result.extend(result_list)

        return result

    def write_file(self, data: List[ProductData], file: Optional[str] = None) -> None:
        if file is None:
            file = self.file
        keys = ProductData.__fields__.keys()
        with open(file, "w", newline='', encoding="utf8") as file:
            writer = csv.writer(file)
            writer.writerow(keys)
            for value in data:
                # нужно тестирование
                writer.writerow(value.dict().values())

    def extract_rating_from_short_info(self, content_category: str, sub_url: str) -> float:
        parser = BeautifulSoup(content_category, "html.parser")

        short_infos = parser.find_all(class_="model-short-info")
        for info in short_infos:
            td = info.find("td")
            a = td.find("a")
            link = a['href']
            if link == sub_url:
                rating_text = info.find(class_="short-opinion-icons")
                if not rating_text.get_text():
                    return -1.0
                bad_face = rating_text.find(class_="l-f-1")
                bad_rating = int(bad_face.sub.get_text())
                neutral_face = rating_text.find(class_="l-f-2")
                neutral_rating = int(neutral_face.sub.get_text())
                good_face = rating_text.find(class_="l-f-3")
                good_rating = int(good_face.sub.get_text())
                great_face = rating_text.find(class_="l-f-4")
                great_rating = int(great_face.sub.get_text())
                logger.info(f"{(bad_rating, neutral_rating, good_rating, great_rating)}")
                avg = avg_rating(bad_rating, neutral_rating, good_rating, great_rating)
                logger.info(f"Avg rating: {avg}")
                return avg

    def extract_pages_count(self, content: str) -> int:
        parser = BeautifulSoup(content, "html.parser")

        result = parser.find(class_="ib page-num")
        result = result.find_all("a")

        result = len(result)

        return result

    async def extract_detailed_info_from_page(self, content: str, slug: str, rating: Optional[float] = None) -> ProductData:
        parser = BeautifulSoup(content, "html.parser")

        # sub_type_ = parser.find(class_="t2 no-mobile ib h1")
        name = parser.find('h1', itemprop="name")
        name = name.get_text()
        logger.info(f"Product name: {name}")
        full_desc = parser.find(class_='desc-ai-title', itemprop='description')
        short_desc = None
        if full_desc:
            if full_desc:
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

        # defining charechteristics
        charc_raw = parser.find("div", class_="m-c-f2")
        if charc_raw:
            # в основном это работает в вьюхах телефона
            charc_list = []
            for charc in charc_raw.find_all("div"):
                title = charc.get('title')
                if title:
                    charc_list.append(title)
        else:
            charc_raw = parser.find("table", class_="one-col")
            charc_raw = charc_raw.find_all("tr", valign="top")

            charc_list = []

            for chrc in charc_raw:
                charc_name = chrc.find("span", class_="nobr ib").get_text()
                charc_values = chrc.find("td", class_="val posr")
                if charc_values:
                    values = []
                    for val in charc_values.find_all("div"):
                        values.append(val.get_text())

                    charc_value = " ".join(values)
                elif charc_value := chrc.find("td", class_="val"):
                    charc_value.get_text()
                charc_list.append(f"{charc_name}{VALUE_SEP}{charc_value}")

        characteristics = SEPARATOR.join(charc_list)

        # seller urls
        url_seller = parser.find(class_="desc-menu").find_all("a")[0]
        url_seller = url_seller['link']

        prices = await (await self.client.get(self.parent_url + url_seller)).text()

        sellers = self.get_sellers(prices)

        catalog_path = parser.find("div", class_="catalog-path s-width").find_all("a")
        category = catalog_path[-2].get_text()

        return ProductData(
            name=name,
            slug=slug,
            rating=rating,
            category=category,
            short_description=short_desc or "",
            characteristics=characteristics,
            tags=tags,
            sellers=sellers,
        )

    def get_sellers(self, content: str) -> List[SellerData]:
        parser = BeautifulSoup(content, "html.parser")

        seller_table = parser.find(class_="where-buy-table")
        # seller_table = seller_table.find("tbody")
        if not seller_table:
            return []
        sellers = seller_table.select('tr[class]')
        result = []
        for seller in sellers:
            name = seller.find(class_='where-buy-description').find('h3').get_text()
            price_td = seller.find(class_='where-buy-price')
            link = price_td.a['href']
            price = price_td.get_text().replace(' ', '')

            # parsing image
            img = seller.find(class_='where-buy-img')
            img = img.find(class_='hide-blacked')
            img = img.find('script').get_text().replace(r"\/", "/")
            img = URL_REGEX.search(img)
            img_url = ""
            if img:
                img_url = img.group(0)

            # parsing color
            color_elem = seller_table.find(class_='where-buy-color')
            color = None
            if color_elem:
                bg_color_elem = color_elem.find('div')
                color = ""
                if bg_color_elem:
                    bg_color = bg_color_elem['style']
                    color = self.get_color_from_style_string(bg_color)

            desc = seller.find(class_='where-buy-description')
            desc = desc.find(class_='it-desc')
            desc_text = ""
            if desc:
                desc_text = desc.get_text()

            price = price.split()
            price.pop(-1)
            price = int("".join(price))

            sell = SellerData(
                name=name,
                link=link,
                price=price,
                img_url=img_url,
                color=color,
                description=desc_text
            )
            result.append(sell)
        return result

    def get_color_from_style_string(self, color: str) -> str:
        """Format: background-color: #ffffff"""
        styles = color.split('\n')
        for style in styles:
            if 'background-color' in style:
                style = style.split(";")
                _, color = style[0].split(":")
                return color

    def get_product_links(self, content: str) -> Set[str]:
        parser = BeautifulSoup(content, "html.parser")
        products = parser.find('form', id='list_form1').select('div[id]')
        links = set()
        for product in products:
            # да
            link = product.find(class_="model-short-title")
            if not link:
                # it selects a div class with and without id
                continue
            link = link.get('href')
            links.add(link)
        return links

    async def close(self) -> None:
        await self.client.close()


def parse_data(urls: Dict[str, str], file: str, limit: int) -> None:
    """
    Парсится дата с е-каталога
    """
    loop = asyncio.get_event_loop()

    parser = Parser(file, urls=urls, limit=limit)
    try:
        data = loop.run_until_complete(parser.get_data())
        logger.info(f"Parser data: {data}")
        parser.write_file(data)
        logger.info("Parser has written data")
    except Exception:
        raise
    finally:
        loop.run_until_complete(parser.close())

import csv
import json
from typing import Tuple

from typing import IO, List

from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine, AsyncEngine

# yeah, I will use them directly
from app.db.repositories import models
from app.db.repositories.product import ProductsCRUD
from app.models.schemas.product import ProductInCreate
from app.models.schemas.product_seller import ProductSellerInCreate
from app.models.schemas.tags import TagsInCreate
from app.services.filler import ModelsFiller
from app.db.engine import get_meta
from .schema import ProductData


class ContentLoader:
    __slots__ = "_session",

    def __init__(self, session: async_sessionmaker) -> None:
        self._session = session

        self._init_env()

    def _init_env(self):
        filler = ModelsFiller()

        ModelsFiller.set_current(filler)

    async def load(self, data: List[ProductData]) -> None:
        async with self._session() as connection:

            for product_data in data:
                tags = product_data.tags
                result_tags = []
                for tag in tags:
                    result_tags.append(TagsInCreate(
                        name=tag,
                    ))
                sellers = product_data.sellers
                result_sellers = []
                for seller in sellers:
                    result_sellers.append(
                        ProductSellerInCreate(
                            description=seller.description,
                            name=seller.name,
                            price=seller.price,
                            link=seller.link,
                        )
                    )

                product_in_create = ProductInCreate(
                    name=product_data.name,
                    tags=result_tags,
                    description=product_data.short_description,
                    category=product_data.category,
                    sellers=result_sellers,
                    slug=product_data.slug[1:] if product_data.slug.startswith("/") else product_data.slug,
                )
                logger.info(f"Loaded {product_in_create.slug}")
                # one by one, which is not so efficient, but it's almost one time code
                _, created = await ProductsCRUD.get_or_create(connection, product_in_create, id_name="slug")
                if created:
                    logger.info(f"{product_in_create.slug} Created")


def create_connection(dsn: str) -> Tuple[async_sessionmaker, AsyncEngine]:
    session = async_sessionmaker(expire_on_commit=True, class_=AsyncSession)

    engine = create_async_engine(dsn)

    session.configure(bind=engine)

    return session, engine


def parse_data(file: IO) -> List[ProductData]:
    reader = csv.reader(file)
    result = []

    # this is because first line is actually metadata
    header = next(reader)
    for i, row in enumerate(reader):
        # сделать два указателя, один на header, один на данные
        product_data = {}

        for j, attribute in enumerate(row):
            json_attribute = attribute.replace("'", '"')
            try:
                data = json.loads(json_attribute)
            except json.JSONDecodeError:
                try:
                    # это ОЧЧЧЕНЬ плохо, по другому я не знаю как
                    data = eval(attribute)
                except (SyntaxError, NameError):
                    data = attribute

            product_data[header[j]] = data

        for key, value in product_data.items():
            if isinstance(value, float):
                if value == -1:
                    product_data[key] = None

        product_data = ProductData(**product_data)
        result.append(product_data)

    return result


async def load_content(file: IO, dsn: str):
    data = parse_data(file)
    session, engine = create_connection(dsn)
    await ContentLoader(session).load(data)
    await engine.dispose()

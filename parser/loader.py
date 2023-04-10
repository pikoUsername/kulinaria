import csv

from typing import IO

# yeah, I will use them directly
from app.db.repositories.product import ProductsCRUD
from .schema import ProductData


class ContentLoader:
    pass


async def create_connection():
    pass


async def load_content(file: IO, dsn: str):
    reader = csv.reader(file)


import asyncio
import pathlib
from typing import Optional

import click
import json

from click import BadParameter
from loguru import logger

from .parser import parse_data as parser_parse_data, TEST_PARSING_URLS
from .consts import DEFAULT_FILE


@click.group()
def cli():
    pass


@cli.command()
@click.option('--file', default=DEFAULT_FILE, type=str)
@click.option('--url-file', default=None, type=str)
@click.option('--limit', "-l", default=5, type=int)
def parse_data(file: str, url_file: Optional[str] = None, limit: int = 5):
    path = pathlib.Path(file).parent
    if path.parent != pathlib.Path(""):
        path.parent.mkdir(exist_ok=True)
    if url_file:
        with open(url_file, "r", encoding="utf8") as file:
            data = json.load(file)
        urls = data
    else:
        urls = TEST_PARSING_URLS

    # все очень плохо 
    parser_parse_data(urls, file, limit=limit)


@cli.command()
@click.option('--file', default=DEFAULT_FILE, type=str)
@click.option('--dsn', type=str)
def load_data(file: str, dsn: str) -> None:
    from .loader import load_content
    if not dsn:
        raise BadParameter("No dsn")

    file = pathlib.Path(file)
    with file.open("r", encoding="utf8") as f:
        if file.suffix != ".csv":
            raise BadParameter("File does not end with .csv suffix")
        asyncio.run(load_content(f, dsn))


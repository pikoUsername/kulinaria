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
def parse_data(file: str, url_file: Optional[str] = None):
    path = pathlib.Path(file).parent
    if path.parent != pathlib.Path(""):
        logger.info("HERE")
        path.parent.mkdir(exist_ok=True)
    if url_file:
        with open(url_file, "r", encoding="utf8") as file:
            data = json.load(file)
        urls = data
    else:
        urls = TEST_PARSING_URLS

    # все очень плохо 
    parser_parse_data(urls, file)


@cli.command()
@click.option('--file', default=DEFAULT_FILE, type=str)
@click.option('--dsn', type=str)
def load_data(file: str, dsn: str) -> None:
    from .loader import load_content

    file = pathlib.Path(file)
    with file.open("r", encoding="utf8") as f:
        if file.suffix != ".csv":
            raise BadParameter("File does not end with .csv suffix")
        load_content(f, dsn)


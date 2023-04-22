import asyncio
import os
import pathlib
from typing import Optional

import click
import json

from click import BadParameter
from dotenv import load_dotenv

from .parser import parse_data as parser_parse_data, TEST_PARSING_URLS
from .consts import DEFAULT_FILE


@click.group()
def cli():
    load_dotenv()


@cli.command()
@click.option('--output', default=DEFAULT_FILE, type=str)
@click.option('--url-file', default=None, type=str)
@click.option('--limit', "-l", default=5, type=int)
def parse_data(output: str, url_file: Optional[str] = None, limit: int = 5):
    if not os.environ["DEBUG"] and not url_file:
        raise click.BadParameter("Debug is true, but url-file is not provided")

    path = pathlib.Path(output).parent
    if path.parent != pathlib.Path(""):
        path.parent.mkdir(exist_ok=True)
    if url_file:
        with open(url_file, "r", encoding="utf8") as file:
            data = json.load(file)
        urls = data
    else:
        urls = TEST_PARSING_URLS

    # все очень плохо 
    parser_parse_data(urls, output, limit=limit)


@cli.command()
@click.option('--file', default=DEFAULT_FILE, type=str)
@click.option('--dsn', type=str)
def load_data(file: str, dsn: str) -> None:
    from .loader import load_content

    file = pathlib.Path(file)
    with file.open("r", encoding="utf8") as f:
        if file.suffix != ".csv":
            raise BadParameter("File does not end with .csv suffix")
        asyncio.run(load_content(f, dsn))


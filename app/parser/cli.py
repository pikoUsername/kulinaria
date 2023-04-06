from typing import Optional

import click
import json

from .parser import parse_data as parser_parse_data, TEST_PARSING_URLS


@click.group()
def cli():
    pass


@cli.command()
@click.option('--file', default='/assets/db.csv', type=str)
@click.option('--url-file', default=None, type=str)
def parse_data(file: str, url_file: Optional[str] = None):
    if url_file:
        with open(url_file, "r", encoding="utf8") as file:
            data = json.load(file)
        urls = data
    else:
        urls = TEST_PARSING_URLS

    # все очень плохо 
    parser_parse_data(urls, file)

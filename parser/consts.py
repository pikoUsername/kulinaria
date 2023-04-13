import re


TEST_PARSING_URLS = {
    "phone": "https://kz.e-katalog.com/list/122/",
    "memory card": "https://kz.e-katalog.com/list/32/",
    "tablets": "https://kz.e-katalog.com/list/30/",
}

SEPARATOR = '\n'
VALUE_SEP = ":"

DEFAULT_FILE = './assets/db.csv'


URL_REGEX = re.compile(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)")
"""
Transliterates from Russian to english alphabet
йцукенгшщзхъфывапролджэячсмитьбю
"""


LOOKUP_TABLE = {
    "а": "a",
    "б": "b",
    "с": "c",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
    "ж": "j",
    "й": "i",
    "и": "i",
    "у": "u",
    "к": "k",
    "ш": "sh",
    "щ": "sh",
    "н": "n",
    "ф": "f",
    "ы": "u",
    "э": "e",
    "я": "ya",
    "ч": "ch",
    "м": "m",
    "т": "t",
    "ц": "cze",
    "з": "ze",
    "х": "h",
    "ъ": "",
    "ь": "",
    "ю": "yo",
    "п": "p",
    "р": "r",
    "о": "o",
    "л": "el",
}


def translate(origin: str) -> str:
    """
    Origin had to be on russian
    This function translates by character to english
    to fit ASCII limitations
    """
    result = []

    for rus_char in origin:
        if rus_char not in LOOKUP_TABLE:
            # idk how to process special characters
            eng_char = rus_char
        else:
            eng_char = LOOKUP_TABLE[rus_char]
        result.append(eng_char)

    return "".join(result)

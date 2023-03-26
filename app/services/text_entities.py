import re

from typing import List, Tuple, Dict
from app.services.enums import TextEntitiesTypes

from app.models.domain import TextEntitiesInDB

# first list is aliases
# second list is tag arguments
ALLOWED_TAGS: Dict[str, Tuple[List[str], TextEntitiesTypes]] = {
	"b": (["bold"], TextEntitiesTypes.bold),
	"u": (["underline"], TextEntitiesTypes.underline),
	"i": (["i"], TextEntitiesTypes),
	# "a": (['a'], ['href'], TextEntitiesTypes.text_link),  # way too hard to implement for now marked as task in TODO list
}


HTML_TAGS_REGEX = re.compile(r"<(?:([A-Za-z0-9][A-Za-z0-9]*)\b[^>]*>(?:.*?)<\/\1>|[A-Za-z0-9][A-Za-z0-9]*\b[^>]*\/>)+")
FIND_TAG = re.compile(r"<(\"[^\"]*\"|'[^']*'|[^'\">])*>")
PHONE_NUMBER_REGEX = re.compile(r"\+([\d]{4})-([\d]{3})-([\d]{4})")
URL_REGEX = re.compile(r"[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)")  # noqa


class Parser:
	"""
	Парсер используется для парсинга текста на отдельные обьекты
	И для выделения html тегов для последуешего хранения и удаления
	нежелетаельных обьектов. Ну и для изображения
	"""
	def __init__(self):
		self.content = ""

	def extract_tag(self, tag_slice: str) -> str:
		return FIND_TAG.search(tag_slice).string

	def validate_tag(self, tag: str) -> bool:
		# detects aliases and checks if the tag is in allowed tags
		try:
			tag_find = ALLOWED_TAGS[tag]
			aliases_in = tag in tag_find[0]
			if aliases_in:
				return True
		except KeyError:
			pass
		return False

	def get_type_by_tag(self, tag: str) -> TextEntitiesTypes:
		# does not check for any KeyError's, use after tag is validated
		return ALLOWED_TAGS[tag][2]

	def parse_entities(self, text: str) -> List[TextEntitiesInDB]:
		self.content = self.content + text
		result = []

		phone_url_matches = [*PHONE_NUMBER_REGEX.finditer(self.content), *URL_REGEX.finditer(self.content)]
		if phone_url_matches:
			for match in phone_url_matches:
				typ = TextEntitiesTypes.phone_number if match.string.startswith("+") else TextEntitiesTypes.url
				entity = TextEntitiesInDB(
					type=typ,
					url=match.string,
					offset=match.start(),
					length=match.end() - match.start(),
				)
				result.append(entity)

		if matches := HTML_TAGS_REGEX.finditer(self.content):
			for match in matches:
				tag = self.extract_tag(match.string)
				assert self.validate_tag(tag), "Tag is not allowed"  # just crashes
				entity = TextEntitiesInDB(
					type=self.get_type_by_tag(tag),
					offset=match.start(),
					length=match.end() - match.start(),
				)
				result.append(entity)

		return result

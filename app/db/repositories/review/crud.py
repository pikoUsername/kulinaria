from app.db.repositories.common import BaseCrud
from app.models.domain import ReviewInDB
from app.models.schemas.review import ReviewInCreate
from .model import Reviews


class ReviewCrud(BaseCrud[Reviews, ReviewInCreate, ReviewInDB]):
	model = Reviews

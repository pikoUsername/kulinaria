from .rwmodel import RWModel
from ..common import IDModelMixin


class CategoryInDB(RWModel, IDModelMixin):
    name: str
    slug: str

from app.services.filler import ModelsFiller

from app.db.engine import get_meta


def test_filler_mixin() -> None:
	filler = ModelsFiller(get_meta())
	filler.set_current(filler)
	filler_ctx = ModelsFiller.get_current()

	assert id(filler) == id(filler_ctx)


def test_filler_resolve() -> None:
	pass


def test_convert_obj_to_model() -> None:
	pass


def test_convert_model_to_obj() -> None:
	pass

from typing import Callable

from fastapi import FastAPI
from loguru import logger

from app.core.settings.app import AppSettings
from app.db.events import close_db_connection, connect_to_db, create_default_permissions, create_default_groups
from app.services.filler import ModelsFiller
from app.db.engine import get_meta


def create_start_app_handler(
		app: FastAPI,
		settings: AppSettings,
) -> Callable:  # type: ignore
	async def start_app() -> None:
		app.state.models_filler = ModelsFiller(get_meta())
		ModelsFiller.set_current(app.state.models_filler)
		await connect_to_db(app, settings)
		await create_default_permissions(app)
		await create_default_groups(app)

	return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:  # type: ignore
	@logger.catch
	async def stop_app() -> None:
		await close_db_connection(app)

	return stop_app

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from dotenv import load_dotenv
import sentry_sdk

from app.api.errors.http_error import http_error_handler
from app.api.errors.validation_error import http422_error_handler
from app.api.routes.api import root_router
from app.core.config import get_app_settings
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.db.repositories import models  # noqa
from app import middlewares
from app.services.filler import ModelsFiller


def get_application() -> FastAPI:
	load_dotenv()
	settings = get_app_settings()

	settings.configure_logging()

	application = FastAPI(**settings.fastapi_kwargs)

	application.state.models_filler = ModelsFiller()
	ModelsFiller.set_current(application.state.models_filler)
	if not settings.debug:
		sentry_sdk.init(
			dsn=settings.sentry_dsn,

			# Set traces_sample_rate to 1.0 to capture 100%
			# of transactions for performance monitoring.
			# We recommend adjusting this value in production.
			traces_sample_rate=1.0
		)

	middlewares.setup(application)

	application.add_event_handler(
		"startup",
		create_start_app_handler(application, settings),
	)
	application.add_event_handler(
		"shutdown",
		create_stop_app_handler(application),
	)

	application.add_exception_handler(HTTPException, http_error_handler)
	application.add_exception_handler(RequestValidationError, http422_error_handler)

	application.include_router(root_router, prefix=settings.api_prefix)

	return application


app = get_application()

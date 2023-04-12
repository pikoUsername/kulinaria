from fastapi import APIRouter, Depends, Body, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED

from app.api.dependencies.database import get_connection
from app.db.repositories.user import UserCrud
from app.models.domain import User
from app.models.schemas.users import UserInResponse, UserWithToken, UserInCreate, UserInLogin

from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.resources import strings
from app.services import jwt, auth

router = APIRouter()


@router.post(
	"/signup",
	status_code=HTTP_201_CREATED,
	name="auth:signup",
)
async def signup(
		user_login: UserInCreate = Body(..., embed=True, alias="user"),
		settings: AppSettings = Depends(get_app_settings),
		session: AsyncSession = Depends(get_connection),
) -> UserInResponse:
	"""
	Gives token using information that user gave

	:return:
	"""
	if await auth.check_email_is_taken(session, user_login.email):
		raise HTTPException(
			status_code=HTTP_400_BAD_REQUEST,
			detail=strings.EMAIL_TAKEN,
		)

	if await auth.check_username_is_taken(session, user_login.username):
		raise HTTPException(
			status_code=HTTP_400_BAD_REQUEST,
			detail=strings.USERNAME_TAKEN,
		)

	user = await UserCrud.create(session, user_login)

	public_user = User(
		username=user.username,
		email=user.email
	)

	token = jwt.create_access_token_for_user(
		public_user,
		secret_key=str(settings.secret_key.get_secret_value()),
	)

	return UserInResponse(
		user=UserWithToken(
			username=user.username,
			email=user.email,
			token=token,
		)
	)


@router.post(
	"/login",
	name="auth:login",
)
async def login(
		user_login: UserInLogin = Body(..., embed=True, alias="user"),
		settings: AppSettings = Depends(get_app_settings),
		session: AsyncSession = Depends(get_connection),
) -> UserInResponse:
	wrong_login_error = HTTPException(
		status_code=HTTP_400_BAD_REQUEST,
		detail=strings.INCORRECT_LOGIN_INPUT,
	)

	user = await UserCrud.get_by_email(session, user_login.email)

	if not user:
		raise wrong_login_error

	if not user.verify_password(user_login.password):
		raise wrong_login_error

	token = jwt.create_access_token_for_user(
		user,
		secret_key=str(settings.secret_key.get_secret_value()),
	)

	return UserInResponse(
		user=UserWithToken(
			token=token,
			username=user.username,
			email=user.email,
			image=user.image_url,
		),
	)

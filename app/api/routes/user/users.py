from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_connection
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.db.repositories.user import UserCrud, Users
from app.models.domain import User as UserPublic
from app.models.schemas.users import UserInResponse, UserInUpdate, UserWithToken
from app.resources import strings
from app.services import jwt
from app.services.auth import check_email_is_taken, check_username_is_taken

router = APIRouter()


@router.get("/{username}", name="users:get-user-profile")
async def retrieve_user_profile(
		username: str,
		session: AsyncSession = Depends(get_connection)
) -> UserPublic:
	user = await UserCrud.get_by_username(session, username)
	if not user:
		raise HTTPException(
			status_code=HTTP_404_NOT_FOUND,
			detail=strings.USER_DOES_NOT_EXIST_ERROR,
		)
	return UserPublic(
		username=user.username,
		email=user.email,
		bio=user.bio,
		lastname=user.lastname,
		address=user.address,
	)


@router.get("/", name="users:get-current-user")
async def retrieve_current_user(
		user: Users = Depends(get_current_user_authorizer()),
		settings: AppSettings = Depends(get_app_settings),
) -> UserInResponse:
	token = jwt.create_access_token_for_user(
		user,
		str(settings.secret_key.get_secret_value()),
	)
	return UserInResponse(
		user=UserWithToken(
			username=user.username,
			email=user.email,
			bio=user.bio,
			image=user.image,
			token=token,
		),
	)


@router.put("/", name="users:update-current-user")
async def update_current_user(
		user_update: UserInUpdate = Body(..., embed=True, alias="user"),
		current_user: UserPublic = Depends(get_current_user_authorizer()),
		settings: AppSettings = Depends(get_app_settings),
		session: AsyncSession = Depends(get_connection),
) -> UserInResponse:
	if user_update.username and user_update.username != current_user.username:
		if await check_username_is_taken(session, user_update.username):
			raise HTTPException(
				status_code=HTTP_400_BAD_REQUEST,
				detail=strings.USERNAME_TAKEN,
			)

	if user_update.email and user_update.email != current_user.email:
		if await check_email_is_taken(session, user_update.email):
			raise HTTPException(
				status_code=HTTP_400_BAD_REQUEST,
				detail=strings.EMAIL_TAKEN,
			)

	user = await UserCrud.update_user(session, current_user, user_update)

	token = jwt.create_access_token_for_user(
		user,
		str(settings.secret_key.get_secret_value()),
	)
	return UserInResponse(
		user=UserWithToken(
			username=user.username,
			email=user.email,
			bio=user.bio,
			image=user.image,
			token=token,
		),
	)

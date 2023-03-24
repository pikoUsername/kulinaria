from pydantic import EmailStr

from app.db.repositories.user import UserCrud, Users
from app.models.domain import UserInDB, User
from app.models.schemas.users import UserInCreate, UserInUpdate

from sqlalchemy.ext.asyncio import AsyncSession


def test_create(db: AsyncSession) -> None:
	user = UserInCreate(
		email=EmailStr("email@gmail.com"),
		username="username",
		password="password1234",
	)
	user_db = await UserCrud.create(db, user)
	assert user_db.username == user.username


def test_get(db: AsyncSession, test_user: Users, test_user_schema: UserInDB) -> None:
	user = await UserCrud.get_by_email(db, test_user_schema.email)
	assert user.email == test_user_schema.email
	user = await UserCrud.get_by_username(db, test_user.username)
	assert user.email == test_user_schema.email


def test_update_user(
		db: AsyncSession,
		test_user: Users,
		test_user_schema: UserInDB
) -> None:
	usr = User(
		email=test_user_schema.email,
		username=test_user_schema.username,
	)
	update_data = UserInUpdate(
		username="Fuck you",
		email="email@gmail.com",
		bio="bio",
	)
	await UserCrud.update_user(db, usr, update_data)


def test_auth(
		db: AsyncSession,
		test_user: Users,
		test_user_schema: UserInDB,
		user_password: str
) -> None:
	auth = await UserCrud.authenticate(
		db,
		email=test_user_schema.email,
		password=user_password,
	)
	assert auth, f"Password: {user_password}, email: {test_user_schema.email}"

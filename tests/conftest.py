import asyncio
from os import environ

import sqlalchemy as sa
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from pydantic import EmailStr
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_meta
from app.db.repositories.user import UserCrud, Users
from app.models.domain.users import UserInDB
from app.models.schemas.users import UserInCreate
from app.services import jwt

environ["APP_ENV"] = "test"


@pytest.fixture
def app() -> FastAPI:
    from app.main import get_application  # local import for testing purpose

    return get_application()


@pytest.fixture
async def initialized_app(app: FastAPI) -> FastAPI:
    async with LifespanManager(app):
        return app


@pytest.fixture
async def db(initialized_app: FastAPI) -> AsyncSession:
    async with initialized_app.state.session() as ses:
        async with ses.begin():
            return ses


@pytest.fixture
async def client(initialized_app: FastAPI) -> AsyncClient:
    async with AsyncClient(
        app=initialized_app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture
def authorization_prefix() -> str:
    from app.core.config import get_app_settings

    settings = get_app_settings()
    jwt_token_prefix = settings.jwt_token_prefix

    return jwt_token_prefix


@pytest.fixture
def test_user_schema() -> UserInDB:
    return UserInDB(
        username="TestUser",
        email=EmailStr("TestUser@gmail.com"),
    )


# garbage
@pytest.fixture
def user_password() -> str:
    return "Test@password"


@pytest.fixture
async def test_user(db: AsyncSession, test_user_schema: UserInDB, user_password: str) -> Users:
    test_user_schema = UserInCreate(
        username=test_user_schema.username,
        email=EmailStr(test_user_schema.email),
        password=user_password,
    )

    user, _ = await UserCrud.get_or_create(db, test_user_schema, id_name="username")
    return user


@pytest.fixture
def token(test_user: UserInDB) -> str:
    return jwt.create_access_token_for_user(test_user, environ["SECRET_KEY"])


@pytest.fixture
def authorized_client(
    client: AsyncClient, token: str, authorization_prefix: str
) -> AsyncClient:
    client.headers = {
        "Authorization": f"{authorization_prefix} {token}",
        **client.headers,
    }
    return client


@pytest.fixture
def example_db_model() -> sa.Table:
    return sa.Table(
        "temp", get_meta(),
        sa.Column("id", sa.Integer, primary_key=True)
    )

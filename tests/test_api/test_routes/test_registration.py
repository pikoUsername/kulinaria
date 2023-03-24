# TODO
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from app.models.domain import UserInDB

pytestmark = pytest.mark.asyncio


async def test_user_success_registration(
    app: FastAPI, client: AsyncClient
) -> None:
    email, username, password = "test@test.com", "username", "password"
    registration_json = {
        "user": {"email": email, "username": username, "password": password}
    }
    response = await client.post(
        app.url_path_for("auth:signup"), json=registration_json
    )
    assert response.status_code == HTTP_201_CREATED


@pytest.mark.parametrize(
    "credentials_part, credentials_value",
    (("username", "free_username"), ("email", "free-email@tset.com")),
)
async def test_failed_user_registration_when_some_credentials_are_taken(
    app: FastAPI,
    client: AsyncClient,
    test_user: UserInDB,
    credentials_part: str,
    credentials_value: str,
) -> None:
    registration_json = {
        "user": {
            "email": "test@test.com",
            "username": "username",
            "password": "password",
        }
    }
    registration_json["user"][credentials_part] = credentials_value

    response = await client.post(
        app.url_path_for("auth:signup"), json=registration_json
    )
    assert response.status_code == HTTP_400_BAD_REQUEST

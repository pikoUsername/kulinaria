from fastapi import APIRouter

from .admin import api as admin_api
from .shop import api as shop_api
from .user import api as user_api


root_router = APIRouter()

root_router.include_router(admin_api.router)
root_router.include_router(shop_api.router)
root_router.include_router(user_api.router)

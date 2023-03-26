from fastapi import APIRouter
from app.api.dependencies.permissions import CheckPermission


router = APIRouter(
	tags=["admin"],
	dependencies=[CheckPermission("*", admin_only=True)]
)

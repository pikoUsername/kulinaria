from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.user import UserCrud, Users


async def check_email_is_taken(db: AsyncSession, email: str) -> bool:
	result = await UserCrud.get_by_email(db, email)
	return bool(result)


async def check_username_is_taken(db: AsyncSession, username: str) -> bool:
	result = await UserCrud.get_by_username(db, username)
	return bool(result)

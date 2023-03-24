from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_connection(request: Request) -> AsyncGenerator[AsyncSession, None]:
	async with request.app.state.session() as ses:
		ses: AsyncSession
		try:
			yield ses
		except:
			await ses.rollback()
			raise
		else:
			await ses.commit()

import asyncio

from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from app.services.cacher import RedisCache

# here will be some global variables,
# not intended to be used in routes, use dependencies instead.
storage = RedisCache(lazy=True)
Meta = MetaData()
Base = declarative_base(metadata=Meta)
Session: sessionmaker = sessionmaker(expire_on_commit=True, class_=AsyncSession)  # noqa
current_session = async_scoped_session(Session, asyncio.current_task)
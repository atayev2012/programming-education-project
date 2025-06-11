from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncAttrs
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from typing import AsyncGenerator, Annotated
from fastapi import Depends
from datetime import datetime

from config import config


engine = create_async_engine(config.get_db_url(), echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


# Dependency -> to create a session for each request
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]

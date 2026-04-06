from __future__ import annotations

from collections.abc import AsyncGenerator
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


@dataclass(frozen=True)
class Database:
    engine: AsyncEngine
    sessionmaker: async_sessionmaker[AsyncSession]

    @classmethod
    def from_url(cls, url: str) -> Database:
        engine = create_async_engine(url, future=True, pool_pre_ping=True)
        maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=engine, expire_on_commit=False, autoflush=False
        )
        return cls(engine=engine, sessionmaker=maker)

    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.sessionmaker() as s:
            yield s

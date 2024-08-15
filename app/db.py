# #############################################
# async postgres session manager, thanks to the following
# https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
# https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308
# #############################################
import logging
import contextlib
from typing import Any, AsyncIterator

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    AsyncConnection,
)


logger = logging.getLogger(__name__)

DB_URL = "postgresql+asyncpg://trace_admin:trace_admin@localhost/trace"


class Base(DeclarativeBase):
    __mapper_args__ = {"eager_defaults": True}


class DBSessionManager:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker | None = None

    def init(self, host: str, engine_kwargs: dict[str, Any] = {}) -> None:
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(
            autocommit=False, bind=self._engine, expire_on_commit=False
        )

    async def close(self):
        if self._engine is None:
            logger.error("The DBSession manager has not yet been initialized.")
            raise Exception("The DBSession manager has not yet been initialized.")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            logger.error("The DBSession manager has not yet been initialized.")
            raise Exception("The DBSession manager has not yet been initialized.")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception as e:
                await connection.rollback()
                logger.error(str(e))
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            logger.error("The DBSession manager has not yet been initialized.")
            raise Exception("The DBSession manager has not yet been initialized.")

        session = self._sessionmaker()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(str(e))
            raise
        finally:
            await session.close()


session_manager = DBSessionManager()


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with session_manager.session() as session:
        yield session

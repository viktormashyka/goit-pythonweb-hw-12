import contextlib
import asyncpg
import asyncio

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings
from src.database.models import Base


async def create_database_if_not_exists():
    conn = await asyncpg.connect(
        user="postgres", password="567234", host="localhost", port=5432
    )
    try:
        await conn.execute("CREATE DATABASE contacts_app")
    except asyncpg.exceptions.DuplicateDatabaseError:
        pass  # Database already exists
    finally:
        await conn.close()


async def create_tables_if_not_exists(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()


async def initialize_database():
    try:
        await create_database_if_not_exists()
    except asyncpg.exceptions.DuplicateDatabaseError:
        pass  # Database already exists

    engine = create_async_engine(settings.DB_URL)
    await create_tables_if_not_exists(engine)


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    async with sessionmanager.session() as session:
        yield session


if __name__ == "__main__":
    asyncio.run(initialize_database())

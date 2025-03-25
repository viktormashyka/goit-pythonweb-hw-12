import sys
import os
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Add the root directory of the project to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from src.database.models import Base, User, UserRole
from src.database.db import get_db
from src.services.auth import create_access_token, Hash

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "deadpool",
    "email": "deadpool@example.com",
    "password": "12345678",
    "role": UserRole.USER,
}

admin_user = {
    "username": "admin",
    "email": "admin@example.com",
    "password": "adminpass",
    "role": UserRole.ADMIN,
}

@pytest_asyncio.fixture(scope="module", autouse=True)
async def init_models_wrap():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        hash_password = Hash().get_password_hash(test_user["password"])
        current_user = User(
            username=test_user["username"],
            email=test_user["email"],
            hashed_password=hash_password,
            confirmed=True,
            avatar="https://twitter.com/gravatar",
        )
        session.add(current_user)

        admin_hash_password = Hash().get_password_hash(admin_user["password"])
        current_admin = User(
            username=admin_user["username"],
            email=admin_user["email"],
            hashed_password=admin_hash_password,
            confirmed=True,
            avatar="https://twitter.com/adminavatar",
            role=UserRole.ADMIN,
        )
        session.add(current_admin)

        await session.commit()

@pytest.fixture(scope="module")
def client():
    # Dependency override
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

@pytest_asyncio.fixture()
async def get_token():
    token = await create_access_token(data={"sub": test_user["username"]})
    return token

@pytest_asyncio.fixture()
async def get_admin_token():
    token = await create_access_token(data={"sub": admin_user["username"]})
    return token
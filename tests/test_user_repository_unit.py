import sys
import os
import pytest

# Add the root directory of the project to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.repositories.users import UserRepository

from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User

from src.schemas import UserCreate

@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session

@pytest.fixture
def users_repository(mock_session):
    return UserRepository(mock_session)

@pytest.fixture
def user():
    return User(id=1, username="testuser", email="test@example.com", hashed_password="hashed_password")

@pytest.mark.asyncio
async def test_create_user(users_repository, mock_session):
    body = UserCreate(username="testuser", email="test@example.com", password="password")
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    user = await users_repository.create_user(body)

    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.hashed_password == "password"

@pytest.mark.asyncio
async def test_get_user_by_id(users_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await users_repository.get_user_by_id(1)

    assert result is not None
    assert result.username == "testuser"

@pytest.mark.asyncio
async def test_get_user_by_username(users_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await users_repository.get_user_by_username("testuser")

    assert result is not None
    assert result.username == "testuser"

@pytest.mark.asyncio
async def test_get_user_by_email(users_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await users_repository.get_user_by_email("test@example.com")

    assert result is not None
    assert result.email == "test@example.com"

@pytest.mark.asyncio
async def test_confirmed_email(users_repository, mock_session, user):
    mock_session.commit = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.scalar_one_or_none = AsyncMock(return_value=user)

    await users_repository.confirmed_email("test@example.com")

    assert user.confirmed is True

@pytest.mark.asyncio
async def test_update_avatar_url(users_repository, mock_session, user):
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.scalar_one_or_none = AsyncMock(return_value=user)

    updated_user = await users_repository.update_avatar_url("test@example.com", "new_avatar_url")

    assert updated_user.avatar == "new_avatar_url"

@pytest.mark.asyncio
async def test_reset_password(users_repository, mock_session, user):
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.scalar_one_or_none = AsyncMock(return_value=user)

    updated_user = await users_repository.reset_password("test@example.com")

    assert updated_user.hashed_password is None

@pytest.mark.asyncio
async def test_update_password(users_repository, mock_session, user):
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.scalar_one_or_none = AsyncMock(return_value=user)

    updated_user = await users_repository.update_password("test@example.com", "new_password")

    assert updated_user.hashed_password == "new_password"
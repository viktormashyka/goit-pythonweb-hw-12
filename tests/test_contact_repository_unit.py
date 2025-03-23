import sys
import os
import pytest

# Add the root directory of the project to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.repositories.contacts import ContactRepository

from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy import select, and_, or_, extract
from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate

@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session

@pytest.fixture
def contacts_repository(mock_session):
    return ContactRepository(mock_session)

@pytest.fixture
def contact():
    return Contact(id=1, first_name="test", last_name="test", email="test@example.com", phone="1234567890", birthday=date.today(), description="test", user_id="testuser")

@pytest.fixture
def user():
    return User(id="testuser")

@pytest.mark.asyncio
async def test_create_contact(contacts_repository, mock_session, user):
    body = ContactModel(first_name="test", last_name="test", email="test@example.com", phone="1234567890", birthday=date.today(), description="description")
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    contact = await contacts_repository.create_contact(body, user)

    assert contact.first_name == "test"
    assert contact.last_name == "test"
    assert contact.email == "test@example.com"
    assert contact.phone == "1234567890"
    assert contact.birthday == date.today()
    assert contact.description == "description"
    assert contact.user_id == user.id

@pytest.mark.asyncio
async def test_get_contact_by_id(contacts_repository, mock_session, contact, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contacts_repository.get_contact_by_id(1, user)

    assert result is not None
    assert result.first_name == "test"

@pytest.mark.asyncio
async def test_get_contacts(contacts_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(id=1, first_name="test_1", last_name="test_1", email="test_1@example.com", phone="1234567890", birthday=date.today(), description="description", user_id="testID_1"),
        Contact(id=2, first_name="test_2", last_name="test_2", email="test_2@example.com", phone="1234567890", birthday=date.today(), description="description", user_id="testID_2")
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contacts_repository.get_contacts(skip=0, limit=10, user=user)

    assert len(contacts) == 2
    assert contacts[0].first_name == "test_1"
    assert contacts[1].first_name == "test_2"

@pytest.mark.asyncio
async def test_update_contact(contacts_repository, mock_session, contact, user):
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.scalar_one_or_none = AsyncMock(return_value=contact)

    body = ContactUpdate(email="new@example.com")

    updated_contact = await contacts_repository.update_contact(contact_id=1, body=body, user=user)

    assert updated_contact.email == "new@example.com"

@pytest.mark.asyncio
async def test_remove_contact(contacts_repository, mock_session, contact, user):
    mock_session.commit = AsyncMock()
    mock_session.delete = AsyncMock()
    mock_session.scalar_one_or_none = AsyncMock(return_value=contact)

    removed_contact = await contacts_repository.remove_contact(contact_id=1, user=user)

    assert removed_contact is not None
    assert removed_contact.id == 1

@pytest.mark.asyncio
async def test_search_contacts(contacts_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(id=1, first_name="test_1", last_name="test_1", email="test_1@example.com", phone="1234567890", birthday=date.today(), description="description", user_id="testID_1")
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contacts_repository.search_contacts(first_name="test_1", last_name=None, email=None, user=user)

    assert len(contacts) == 1
    assert contacts[0].first_name == "test_1"

@pytest.mark.asyncio
async def test_get_upcoming_birthdays(contacts_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(id=1, first_name="test_1", last_name="test_1", email="test_1@example.com", phone="1234567890", birthday=date.today() + timedelta(days=1), description="description", user_id="testID_1")
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contacts_repository.get_upcoming_birthdays(user=user)

    assert len(contacts) == 1
    assert contacts[0].first_name == "test_1"
import pytest

from src.repositories.contacts import ContactRepository

from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
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
async def test_get_contacts(contacts_repository, mock_session, contact, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contacts_repository.get_contacts(0, 10, user)

    assert len(contacts) == 1
    assert contacts[0].first_name == "test"


@pytest.mark.asyncio
async def test_update_contact(contacts_repository, mock_session, contact, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    body = ContactUpdate(email="new@example.com")

    updated_contact = await contacts_repository.update_contact(contact.id, body, user)

    assert isinstance(updated_contact, Contact)
    assert updated_contact.first_name == contact.first_name
    assert updated_contact.last_name == contact.last_name
    assert updated_contact.email == "new@example.com"
    assert updated_contact.phone == contact.phone
    assert updated_contact.birthday == contact.birthday
    assert updated_contact.description == contact.description

    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(contact)


@pytest.mark.asyncio
async def test_remove_contact(contacts_repository, mock_session, contact, user):
    mock_session.commit = AsyncMock()
    mock_session.scalar_one_or_none = AsyncMock(return_value=contact)
    contacts_repository.db.session = mock_session

    await contacts_repository.remove_contact(contact.id, user)

    mock_session.commit.assert_called_once()


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
async def test_get_upcoming_birthdays(contacts_repository, mock_session, contact, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    upcoming_birthdays = await contacts_repository.get_upcoming_birthdays(user)

    assert len(upcoming_birthdays) == 1
    assert upcoming_birthdays[0].first_name == "test"
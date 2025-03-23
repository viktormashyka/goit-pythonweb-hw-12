from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import select, and_, or_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate


class ContactRepository:
    """
    Repository for managing contacts in the database.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.

        :param session: The database session.
        :type session: AsyncSession
        """
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Retrieve a list of contacts for a user with pagination.

        :param skip: The number of records to skip.
        :type skip: int
        :param limit: The maximum number of records to return.
        :type limit: int
        :param user: The user to retrieve contacts for.
        :type user: User
        :return: A list of contacts.
        :rtype: List[Contact]
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieve a contact by its ID for a specific user.

        :param contact_id: The ID of the contact.
        :type contact_id: int
        :param user: The user to retrieve the contact for.
        :type user: User
        :return: The contact if found, otherwise None.
        :rtype: Contact | None
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Create a new contact for a user.

        :param body: The contact data.
        :type body: ContactModel
        :param user: The user to create the contact for.
        :type user: User
        :return: The created contact.
        :rtype: Contact
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Remove a contact by its ID for a specific user.

        :param contact_id: The ID of the contact.
        :type contact_id: int
        :param user: The user to remove the contact for.
        :type user: User
        :return: The removed contact if found, otherwise None.
        :rtype: Contact | None
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate, user: User
    ) -> Contact | None:
        """
        Update a contact by its ID for a specific user.

        :param contact_id: The ID of the contact.
        :type contact_id: int
        :param body: The updated contact data.
        :type body: ContactUpdate
        :param user: The user to update the contact for.
        :type user: User
        :return: The updated contact if found, otherwise None.
        :rtype: Contact | None
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def search_contacts(
        self,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
        user: User,
    ) -> List[Contact]:
        """
        Search for contacts by first name, last name, and email for a specific user.

        :param first_name: The first name to search for.
        :type first_name: Optional[str]
        :param last_name: The last name to search for.
        :type last_name: Optional[str]
        :param email: The email to search for.
        :type email: Optional[str]
        :param user: The user to search contacts for.
        :type user: User
        :return: A list of contacts matching the search criteria.
        :rtype: List[Contact]
        """
        stmt = select(Contact).filter(
            and_(
                Contact.user_id == user.id,
                Contact.first_name.ilike(f"%{first_name}%") if first_name else True,
                Contact.last_name.ilike(f"%{last_name}%") if last_name else True,
                Contact.email.ilike(f"%{email}%") if email else True,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_upcoming_birthdays(self, user: User) -> List[Contact]:
        """
        Retrieve contacts with upcoming birthdays within the next week for a specific user.

        :param user: The user to retrieve upcoming birthdays for.
        :type user: User
        :return: A list of contacts with upcoming birthdays.
        :rtype: List[Contact]
        """
        today = date.today()
        next_week = today + timedelta(days=7)
        stmt = select(Contact).filter(
            and_(
                Contact.user_id == user.id,
                or_(
                    and_(
                        extract("month", Contact.birthday) == today.month,
                        extract("day", Contact.birthday) >= today.day,
                    ),
                    and_(
                        extract("month", Contact.birthday) == next_week.month,
                        extract("day", Contact.birthday) <= next_week.day,
                    ),
                ),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

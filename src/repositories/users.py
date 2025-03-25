from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    """
    Repository for performing CRUD operations on User model.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the UserRepository with a database session.

        :param session: AsyncSession object for database interaction.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.

        :param user_id: ID of the user to retrieve.
        :return: User object if found, else None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.

        :param username: Username of the user to retrieve.
        :return: User object if found, else None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email.

        :param email: Email of the user to retrieve.
        :return: User object if found, else None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new user.

        :param body: UserCreate schema object containing user details.
        :param avatar: Optional avatar URL for the user.
        :return: The created User object.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Confirm a user's email.

        :param email: Email of the user to confirm.
        """
        user = await self.get_user_by_email(email)
        if user:
            user.confirmed = True
            await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update a user's avatar URL.

        :param email: Email of the user to update.
        :param url: New avatar URL.
        :return: The updated User object.
        """
        user = await self.get_user_by_email(email)
        if user:
            user.avatar = url
            await self.db.commit()
            await self.db.refresh(user)
            return user

    async def reset_password(self, email: str) -> User:
        """
        Reset a user's password.

        :param email: Email of the user to reset password.
        :return: The updated User object with password reset.
        """
        user = await self.get_user_by_email(email)
        if user:
            user.hashed_password = None
            await self.db.commit()
            await self.db.refresh(user)
            return user

    async def update_password(self, email: str, password: str) -> User:
        """
        Update a user's password.

        :param email: Email of the user to update password.
        :param password: New password.
        :return: The updated User object with new password.
        """
        user = await self.get_user_by_email(email)
        if user:
            user.hashed_password = password
            await self.db.commit()
            await self.db.refresh(user)
            return user
from sqlalchemy import Column, Integer, String, Boolean, Date, func, Enum as SqlEnum
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from enum import Enum


class Base(DeclarativeBase):
    pass

class UserRole(str, Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    description = Column(String, nullable=True)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="contacts")

    def __repr__(self):
        return f"<Contact(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, phone={self.phone}, birthday={self.birthday}, description={self.description}), user_id={self.user_id}>"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)


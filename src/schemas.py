from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from src.database.models import UserRole


class ContactModel(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: str = Field(max_length=50)
    phone: str = Field(max_length=13)
    birthday: date
    description: Optional[str] = Field(None, max_length=150)


class ContactResponse(ContactModel):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ContactUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=13)
    birthday: Optional[date] = Field(None)
    description: Optional[str] = Field(None, max_length=150)


class ContactRemove(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Схема користувача
class User(BaseModel):
    id: int
    username: str
    email: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)


# Схема для запиту реєстрації
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(User):
    id: int
    username: str
    email: str
    avatar: str | None
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserUpdatePassword(BaseModel):
    password: str


# Схема для токену
class Token(BaseModel):
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr

from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from fastapi import Depends, HTTPException

from src.repositories.users import UserRepository
from src.schemas import UserCreate

from src.database.db import get_db

from src.services.auth import get_current_user
from src.database.models import User, UserRole

from src.services.auth import AuthService, oauth2_scheme, get_current_user
from src.services.users import UserService

def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)


def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.get_current_user(token)

# Залежності для перевірки ролей
def get_current_moderator_user(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Недостатньо прав доступу")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Недостатньо прав доступу")
    return current_user
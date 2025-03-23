from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends, HTTPException

from src.database.db import get_db

from src.services.auth import get_current_user
from src.database.models import User, UserRole

from src.services.auth import oauth2_scheme, get_current_user as get_current_user_auth


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    return await get_current_user_auth(token=token, db=db)


def get_current_moderator_user(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Недостатньо прав доступу")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Недостатньо прав доступу")
    return current_user

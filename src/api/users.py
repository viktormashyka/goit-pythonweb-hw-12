from fastapi import APIRouter, Depends, Request, File, UploadFile, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.users import UserService
from src.services.upload_file import UploadFileService
from src.services.dependencies import get_current_moderator_user, get_current_admin_user

from src.conf.config import settings
from src.database.db import get_db
from src.database.models import User, UserRole

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.schemas import UserResponse
from src.services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me",
    response_model=UserResponse,
    description="No more than 10 requests per minute",
)
@limiter.limit("10/minute")
async def me(request: Request, user: UserResponse = Depends(get_current_user)):
    return user


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Недостатньо прав доступу для виконання цієї дії"
        )

    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user


@router.get("/moderator")
def read_moderator(
    current_user: User = Depends(get_current_moderator_user),
):
    return {
        "message": f"Вітаємо, {current_user.username}! Це маршрут для модераторів та адміністраторів"
    }


@router.get("/admin")
def read_admin(current_user: User = Depends(get_current_admin_user)):
    return {"message": f"Вітаємо, {current_user.username}! Це адміністративний маршрут"}

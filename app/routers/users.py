from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.user import User
from app.database.deps import get_db
from app.services import user_service
from typing import List
from app.auth.auth_utils import get_current_user, get_current_user_id, get_password_hash

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(user_update: UserUpdate, db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    if user_update.username and user_update.username != current_user.username:
        existing_user = await db.execute(select(User).where(User.username == user_update.username))

        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username already in use")

    if user_update.email and user_update.email != current_user.email:
        existing_email = await db.execute(select(User).where(User.email == user_update.email))
        if existing_email.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    update_data = user_update.model_dump(exclude_unset=True)

    if "password" in update_data:
        plain = update_data.pop("password")
        update_data["password"] = get_password_hash(plain)

    for field, value in update_data.items():
        setattr(current_user, field, value)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/", response_model=List[UserResponse])
async def read_user(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await user_service.get_users(db, skip=skip, limit=limit)


@router.get("/{username}", response_model=List[UserResponse])
async def search_users(username: str, db: AsyncSession = Depends(get_db), limit: int = 100,
                       current_user_id: int = Depends(get_current_user_id)):
    user = await user_service.search_user_by_username(db, username, limit)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),):
    success = await user_service.delete_user(db, current_user, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None

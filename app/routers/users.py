from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.user import User
from app.database.deps import get_db
from app.services import user_service
from typing import List


router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db))->User:
    if await user_service.get_user_by_username(db, user.name):
        raise HTTPException(status_code=409, detail="Username already taken")
    if await user_service.get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail="Email already in use")
    return await user_service.create_user(db, user)



@router.get("/", response_model=List[UserResponse])
async def read_user(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await user_service.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await user_service.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=409, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    success = await user_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None




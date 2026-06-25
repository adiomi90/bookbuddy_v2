from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.models.post import Post
from app.auth.auth_utils import get_current_user_id
from app.services import post_service
from app.routers.auth import get_db
from typing import List


router = APIRouter()


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: AsyncSession = Depends(get_db),
                      user_id: int = Depends(get_current_user_id)) -> Post:
    return await post_service.create_post(db, user_id, post)


@router.get("/", response_model=List[PostResponse])
async def get_all_post(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await post_service.get_all_post(db, skip=skip, limit=limit)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post_by_id(post_id: int, db: AsyncSession = Depends(get_db),
                         user_id: int = Depends(get_current_user_id)):
    return await post_service.get_post_by_id(db, post_id)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_update: PostUpdate, db: AsyncSession = Depends(get_db),
                      user_id: int = Depends(get_current_user_id)):
    return await post_service.update_post(db, post_id, post_update, user_id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db),
                      user_id: int = Depends(get_current_user_id)):
    return await post_service.delete_post(db, post_id, user_id)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.models.post import Post
from app.database.deps import get_db
from app.services import post_service
from typing import List

#temporary Dependency
async def get_current_user_id(db: AsyncSession = Depends(get_db)) -> int:
    from sqlalchemy import select
    from app.models.user import User
    result = await db.execute(select(User.id).where(User.id == 3).limit(1))
    user_id = result.scalar_one_or_none()
    if not user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No user found , Please create a user")
    return user_id


router = APIRouter()


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: AsyncSession = Depends(get_db),
                      user_id: int = Depends(get_current_user_id))->Post:
    return await post_service.create_post(db, user_id, post)


@router.get("/", response_model=List[PostResponse])
async def get_all_post(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await post_service.get_all_post(db, skip=skip, limit=limit)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post_by_id(post_id: int, db: AsyncSession = Depends(get_db)):
    return await post_service.get_post_by_id(db, post_id)

@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_update: PostUpdate, db: AsyncSession = Depends(get_db),
                      user_id: int = Depends(get_current_user_id)):
    return await post_service.update_post(db, post_id, post_update, user_id)
    
@router.delete("/{post_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db),
                      user_id: int = Depends(get_current_user_id)):
    return await post_service.delete_post(db, post_id, user_id)





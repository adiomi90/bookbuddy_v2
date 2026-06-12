from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate
from typing import List
from app.services.user_service import get_user
from fastapi import HTTPException, status


async def get_all_post(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Post]:
    result = await db.execute(select(Post).offset(skip).limit(limit))
    return result.scalars().all()


async def get_post_by_id(db: AsyncSession, post_id: int) -> Post | None:
    result = await db.execute(select(Post).where(Post.id == post_id))
    return result.scalar_one_or_none()


async def create_post(db: AsyncSession, user_id: int, post: PostCreate) -> Post:
    db_user = await get_user(db, user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized")

    db_post = Post(**post.model_dump(), user_id=user_id)
    db.add(db_post)

    await db.commit()
    await db.refresh(db_post)
    return db_post


async def update_post(db: AsyncSession, post_id: int, post_update: PostUpdate, user_id: int) -> Post | None:
    post = await get_post_by_id(db, post_id)
    if not post or post.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Post not found or Not Authorized")

    update_post = post_update.model_dump(exclude_unset=True)
    for field, value in update_post.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(db: AsyncSession, post_id: int, user_id: int) -> bool:
    post = await get_post_by_id(db, post_id)
    if not post or post.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Post not found or Not Authorized")

    await db.delete(post)
    await db.commit()
    return True

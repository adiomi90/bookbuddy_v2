from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from typing import List
from app.services.user_service import get_user
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload


async def get_all_comments_for_post(db: AsyncSession, post_id: int, skip: int = 1, limit: int = 100) -> List[Comment]:
    stmt = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at).offset(skip).limit(limit)
    )
    result = await db.execute(stmt)
    comments = result.scalars().all()

    return comments


async def get_comment_by_id(db: AsyncSession, comment_id: int) -> Comment | None:
    stmt = (
        select(Comment)
        .where(Comment.id == comment_id))

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_comment(db: AsyncSession, comment: CommentCreate, user_id: int, ) -> Comment:
    db_comment = Comment(
        content=comment.content,
        user_id=user_id,
        post_id=comment.post_id
    )

    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)

    return db_comment


async def update_comment(db: AsyncSession, comment_id: int, comment_update: CommentUpdate, user_id: int) -> Comment | None:
    comment = await get_comment_by_id(db, comment_id)
    if not comment or comment.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Post not found or Not Authorized")

    update_data = comment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)

    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(db: AsyncSession, comment_id: int, user_id: int) -> bool:
    comment = await get_comment_by_id(db, comment_id)
    if not comment or comment.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Post not found or Not Authorized")
    await db.delete(comment)
    await db.commit()
    return True


async def delete_comment_as_admin(db: AsyncSession, comment_id: int) -> bool:
    comment = await get_comment_by_id(db, comment_id)

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No comment found")
    await db.delete(comment)
    await db.commit()
    return True

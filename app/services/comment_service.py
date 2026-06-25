from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate
from typing import List
from app.services.user_service import get_user
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload, attributes

from sqlalchemy.orm import attributes, selectinload


async def get_comment_by_id(db: AsyncSession, comment_id: int) -> Comment | None:
    # 1. Get the comment itself (with owner)
    stmt = (
        select(Comment)
        .where(Comment.id == comment_id)
        .options(selectinload(Comment.owner))
    )
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    if not comment:
        return None

    # 2. Load its immediate replies (with owners)
    replies_stmt = (
        select(Comment)
        .where(Comment.parent_id == comment_id)
        .options(selectinload(Comment.owner))
        .order_by(Comment.created_at)
    )
    replies_result = await db.execute(replies_stmt)
    replies = replies_result.scalars().all()

    # 3. For each reply, ensure its own replies attribute is an empty list
    for reply in replies:
        attributes.set_committed_value(reply, 'replies', [])

    # 4. Assign the replies list to the main comment
    attributes.set_committed_value(comment, 'replies', replies)
    return comment


async def get_comments_with_relations(
    db: AsyncSession,
    post_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[Comment]:
    # 1. Get top‑level comments (with owners)
    stmt = (
        select(Comment)
        .where(Comment.post_id == post_id, Comment.parent_id.is_(None))
        .options(selectinload(Comment.owner))
        .order_by(Comment.created_at)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    top_comments = result.scalars().all()

    if not top_comments:
        return []

    # 2. Fetch all replies for these top comments (with owners)
    top_ids = [c.id for c in top_comments]
    replies_stmt = (
        select(Comment)
        .where(Comment.parent_id.in_(top_ids))
        .options(selectinload(Comment.owner))
        .order_by(Comment.created_at)
    )
    replies_result = await db.execute(replies_stmt)
    all_replies = replies_result.scalars().all()

    # 3. For each reply, set its replies attribute to an empty list
    for reply in all_replies:
        attributes.set_committed_value(reply, 'replies', [])

    # 4. Group replies by parent_id
    replies_by_parent = {cid: [] for cid in top_ids}
    for reply in all_replies:
        replies_by_parent.setdefault(reply.parent_id, []).append(reply)

    # 5. Assign the grouped replies to each top‑level comment
    for comment in top_comments:
        attributes.set_committed_value(
            comment,
            'replies',
            replies_by_parent.get(comment.id, [])
        )

    return top_comments


async def create_comment(db: AsyncSession, comment: CommentCreate, user_id: int) -> Comment:

    if comment.parent_id is not None:
        parent = await get_comment_by_id(db, comment.parent_id)
        if not parent or parent.post_id != comment.post_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Invalid parent comment")

    db_comment = Comment(
        content=comment.content,
        user_id=user_id,
        post_id=comment.post_id,
        parent_id=comment.parent_id
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

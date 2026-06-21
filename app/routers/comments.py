from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.models.comment import Comment
from app.database.deps import get_db
from app.services import comment_service
from typing import List
from app.auth.auth_utils import get_current_user_id

router = APIRouter()


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(comment: CommentCreate, db: AsyncSession = Depends(get_db),
                         user_id: int = Depends(get_current_user_id)) -> Comment:
    return await comment_service.create_comment(db, comment, user_id)


@router.get("/post/{post_id}", response_model=List[CommentResponse])
async def get_all_comments_on_post(post_id: int, skip: int = 0, limit: int = 100,
                                    db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    return await comment_service.get_all_comments_for_post(db, post_id, skip, limit)


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment_by_id(comment_id: int, db: AsyncSession = Depends(get_db),
                             user_id: int = Depends(get_current_user_id)):
    return await comment_service.get_comment_by_id(db, comment_id)


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, comment_update: CommentUpdate, db: AsyncSession = Depends(get_db),
                         user_id: int = Depends(get_current_user_id)):
    return await comment_service.update_comment(db, comment_id, comment_update, user_id)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    return await comment_service.delete_comment(db, comment_id,user_id)

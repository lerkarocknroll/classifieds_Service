from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app import schemas, services, models
from app.dependencies import get_db_session, get_current_user, get_current_user_optional

router = APIRouter(prefix="/user", tags=["Users"])

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: schemas.UserCreate,
    session: AsyncSession = Depends(get_db_session)
):
    return await services.create_user(session, user_data)

@router.get("/", response_model=List[schemas.UserResponse])
async def get_users(
    session: AsyncSession = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user)
):
#Получение списка всех пользователей (только для администраторов)
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    users = await services.get_all_users(session)
    return users

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    user = await services.get_item(session, models.User, user_id)
    return user

@router.patch("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int,
    update_data: schemas.UserUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await services.update_user(session, user_id, update_data)

@router.delete("/{user_id}", response_model=schemas.OKResponse)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    await services.delete_item(session, models.User, user_id)
    return schemas.OKResponse()
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional, List
from app import models, schemas
from app.auth import get_password_hash

#Общие CRUD
async def add_item(session: AsyncSession, orm_model: type, item_data):
    new_item = orm_model(**item_data.model_dump())
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)
    return new_item

async def get_item(session: AsyncSession, orm_model: type, item_id: int):
    stmt = select(orm_model).where(orm_model.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{orm_model.__name__} with id {item_id} not found"
        )
    return item

async def update_item(session: AsyncSession, orm_model: type, item_id: int, update_data):
    item = await get_item(session, orm_model, item_id)
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(item, key, value)
    await session.commit()
    await session.refresh(item)
    return item

async def delete_item(session: AsyncSession, orm_model: type, item_id: int) -> None:
    item = await get_item(session, orm_model, item_id)
    await session.delete(item)
    await session.commit()

#Пользователи
async def get_user_by_username(session: AsyncSession, username: str):
    stmt = select(models.User).where(models.User.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_by_email(session: AsyncSession, email: str):
    stmt = select(models.User).where(models.User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_all_users(session: AsyncSession) -> List[models.User]:
    result = await session.execute(select(models.User))
    return result.scalars().all()

async def create_user(session: AsyncSession, user_data: schemas.UserCreate):
    existing = await get_user_by_username(session, user_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    existing = await get_user_by_email(session, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = get_password_hash(user_data.password)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed,
        role="user"
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

async def update_user(session: AsyncSession, user_id: int, update_data: schemas.UserUpdate):
    user = await get_item(session, models.User, user_id)
    update_dict = update_data.model_dump(exclude_unset=True)

    # Проверка уникальности username
    if "username" in update_dict and update_dict["username"] != user.username:
        existing = await get_user_by_username(session, update_dict["username"])
        if existing:
            raise HTTPException(status_code=400, detail="Username already registered")

    # Проверка уникальности email
    if "email" in update_dict and update_dict["email"] != user.email:
        existing = await get_user_by_email(session, update_dict["email"])
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

    if "password" in update_dict:
        update_dict["hashed_password"] = get_password_hash(update_dict.pop("password"))

    for key, value in update_dict.items():
        setattr(user, key, value)

    await session.commit()
    await session.refresh(user)
    return user

#Объявления
async def create_advertisement(session: AsyncSession, ad_data: schemas.AdvertisementCreate, user_id: int):
    new_ad = models.Advertisement(
        title=ad_data.title,
        description=ad_data.description,
        price=ad_data.price,
        user_id=user_id
    )
    session.add(new_ad)
    await session.commit()
    await session.refresh(new_ad)
    return new_ad

async def get_advertisements(
    session: AsyncSession,
    title: Optional[str] = None,
    description: Optional[str] = None,
    author: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.Advertisement]:
    query = select(models.Advertisement).join(models.User)
    if title:
        query = query.where(models.Advertisement.title.contains(title))
    if description:
        query = query.where(models.Advertisement.description.contains(description))
    if author:
        query = query.where(models.User.username.contains(author))
    if price_min is not None:
        query = query.where(models.Advertisement.price >= price_min)
    if price_max is not None:
        query = query.where(models.Advertisement.price <= price_max)
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()
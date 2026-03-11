from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app import schemas, services, models
from app.dependencies import get_db_session, get_current_user, get_current_user_optional

router = APIRouter(prefix="/advertisement", tags=["Advertisements"])

@router.post("/", response_model=schemas.AdvertisementResponse, status_code=status.HTTP_201_CREATED)
async def create_advertisement(
    ad_data: schemas.AdvertisementCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user)
):
    new_ad = await services.create_advertisement(session, ad_data, current_user.id)
    return new_ad

@router.get("/{ad_id}", response_model=schemas.AdvertisementResponse)
async def get_advertisement(
    ad_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    ad = await services.get_item(session, models.Advertisement, ad_id)
    return ad

@router.patch("/{ad_id}", response_model=schemas.AdvertisementResponse)
async def update_advertisement(
    ad_id: int,
    ad_update: schemas.AdvertisementUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user)
):
    ad = await services.get_item(session, models.Advertisement, ad_id)
    if current_user.role != "admin" and ad.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    updated_ad = await services.update_item(session, models.Advertisement, ad_id, ad_update)
    return updated_ad

@router.delete("/{ad_id}", response_model=schemas.OKResponse)
async def delete_advertisement(
    ad_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user)
):
    ad = await services.get_item(session, models.Advertisement, ad_id)
    if current_user.role != "admin" and ad.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    await services.delete_item(session, models.Advertisement, ad_id)
    return schemas.OKResponse()

@router.get("/", response_model=List[schemas.AdvertisementResponse])
async def search_advertisements(
    session: AsyncSession = Depends(get_db_session),
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    author: Optional[str] = Query(None, description="Фильтр по имени автора"),
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    ads = await services.get_advertisements(
        session,
        title=title,
        description=description,
        author=author,
        price_min=price_min,
        price_max=price_max,
        skip=skip,
        limit=limit
    )
    return ads
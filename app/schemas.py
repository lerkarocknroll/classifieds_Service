from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime

# Пользователи
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Объявления
class AdvertisementBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float

class AdvertisementCreate(AdvertisementBase):
    pass

class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class AdvertisementResponse(AdvertisementBase):
    id: int
    author: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Общие
class OKResponse(BaseModel):
    status: str = "ok"

# Аутентификация
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.lifespan import lifespan
from app import schemas, models, services
from app.dependencies import get_db_session
from app.auth import authenticate_user, create_access_token
from app.routers import users, advertisements

app = FastAPI(
    title="Advertisements Service",
    description="Service for buying/selling advertisements with user management",
    version="0.2.0",
    lifespan=lifespan
)

app.include_router(users.router)
app.include_router(advertisements.router)

@app.post("/login", response_model=schemas.TokenResponse)
async def login(
    login_data: schemas.LoginRequest,
    session: AsyncSession = Depends(get_db_session)
):
    user = await authenticate_user(login_data.username, login_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return schemas.TokenResponse(access_token=access_token)
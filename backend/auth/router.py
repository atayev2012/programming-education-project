from fastapi import APIRouter, Depends, Response, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth.schemas import UserLogin
from models import User
from database import SessionDep
from sqlalchemy import select
from auth.utils import verify_password, create_token, get_username_from_token, get_user_by_username
from config import config
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/auth", tags=["auth"])

# create new user
@router.post("/sign_up")
async def sign_up():
    pass

@router.post("/token")
async def login(form_data: UserLogin, response: Response, session: SessionDep):
    statement = select(User).filter(User.username == form_data.username)
    user_data = await session.execute(statement)
    user = user_data.scalar_one_or_none()
    verification_result = verify_password(form_data.password, user.password_hash)
    
    
    # if not user or user['password'] != form_data.password:
    #     raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # token = create_access_token(form_data.username)

    if verification_result:
        access_token = create_token({"username":user.username})
        refresh_token = create_token({"username":user.username}, type="refresh")
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True,  # Makes the cookie HTTP-only (cannot be accessed via JavaScript)
        secure=True,  # Use secure flag for HTTPS connections
        max_age=timedelta(minutes=config.JWT_EXPIRATION_TIME),  # Expiration time
        expires=datetime.now(timezone.utc) + timedelta(minutes=config.JWT_EXPIRATION_TIME)  # Cookie expiration
    )

    response.set_cookie(
        key="refresh_token", 
        value=refresh_token, 
        httponly=True,  # Makes the cookie HTTP-only (cannot be accessed via JavaScript)
        secure=True,  # Use secure flag for HTTPS connections
        max_age=timedelta(days=config.JWT_REFRESH_EXPIRATION_TIME),  # Expiration time
        expires=datetime.now(timezone.utc) + timedelta(days=config.JWT_REFRESH_EXPIRATION_TIME)  # Cookie expiration
    )

    return {"access_token": access_token, "token_type": "bearer" } #{"access_token": token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}


@router.get("/users/me")
async def read_users_me(user = Depends(get_user_by_username)):

    return {"message": "This is the user information", "username": user}
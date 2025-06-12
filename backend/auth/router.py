from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth.schemas import UserLogin, UserSignUp
from models import User
from database import SessionDep
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from auth.utils import (verify_password, create_token, get_password_hash, 
                        get_user_by_username, set_token_to_cookies)
from config import config
from datetime import datetime, timedelta, timezone



router = APIRouter(prefix="/auth", tags=["auth"])

# create new user
@router.post("/sign_up", status_code=status.HTTP_201_CREATED)
async def sign_up(user_data: UserSignUp, response: Response, session: SessionDep):  
    user_data_dict = user_data.model_dump()
    user_data_dict.setdefault("password_hash", get_password_hash(user_data_dict["password"]))
    user_data_dict.pop("password")
    user = User(**user_data_dict)
    try:
        session.add(user)
        await session.commit()
    except IntegrityError as e:
        error_data = str(e.orig).split("DETAIL")[1]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": f"Integrity constraint violation{error_data}"
            })
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Server internal error occured. Try again later."
            })
    
    # create tokens for user
    access_token = create_token({"username": user.username}, type="access")
    refresh_token = create_token({"username": user.username}, type="refresh")

    await set_token_to_cookies(access_token, "access", response)
    await set_token_to_cookies(refresh_token, "refresh", response)

    return_value = {
        "success": True,
        "message": "New user was successfully created",
        "details": user
    }

    return return_value


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
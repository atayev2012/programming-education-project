from fastapi import APIRouter, Depends, Response, Request, HTTPException, status, BackgroundTasks
from auth.schemas import UserLogin, UserSignUp, BaseUser
from models import User
from database import SessionDep
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from auth.utils import (verify_password, create_token, get_password_hash, 
                        get_user_by_username, set_token_to_cookies,
                        send_email_verification_token, get_username)
from config import config


router = APIRouter(prefix="/auth", tags=["auth"])

# create new user endpoint
@router.post("/sign_up", status_code=status.HTTP_201_CREATED)
async def sign_up(user_data: UserSignUp, response: Response, session: SessionDep, background_tasks: BackgroundTasks):  
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
        "detail":{
            "success": True,
            "message": "New user was successfully created. Email verification link was sent to your address.",
            "data": {
                "username": user.username,
                "email": user.email
            }
        }
    }

    # send email in background
    background_tasks.add_task(send_email_verification_token, user)

    return return_value


# login endpoint
@router.post("/sign_in")
async def sign_in(form_data: UserLogin, response: Response, session: SessionDep):
    statement = select(User).filter(User.username == form_data.username)
    try:
        user_data = await session.execute(statement)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Server internal error occured. Try again later."
            })
    user = user_data.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": f"User with username {form_data.username} was not found."
            }
        )

    verification_result = verify_password(form_data.password, user.password_hash)

    if verification_result:
        access_token = create_token({"username":user.username})
        refresh_token = create_token({"username":user.username}, type="refresh")
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Wrong password",
                "data": None
            }
        )
    
    await set_token_to_cookies(access_token, "access", response)
    await set_token_to_cookies(refresh_token, "refresh", response)

    return_value = {
        "detail": {
            "success": True,
            "message": f"User with username {form_data.username} successfully signed in.",
            "data": None
        }
    }
    return return_value

# logout endpoint
@router.post("/sign_out")
async def sign_out(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {
        "detail": {
            "success": True,
            "message": "User signed out successfully",
            "data": None
        }
    }

# get current user
@router.get("/active_user")
async def active_user(user = Depends(get_user_by_username)):
    return {
        "details": {
            "success": True,
            "message": f"User is authenticated",
            "data": BaseUser.model_validate(user)
        }
    }

@router.get("/email_verify/{verify_token}")
async def email_verify(verify_token, session: SessionDep):
    username = await get_username(verify_token, secret_key=config.EMAIL_VERIFICATION_SECRET_KEY)
    user = await get_user_by_username(session=session, username=username)
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "Email was already verified.",
                "data": None
            }
        )
    
    user.email_verified = True

    try:
        await session.commit()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Server internal error occured. Try again later.",
                "data": None
            }
        )
    
    return_value = {
        "success": True,
        "message": f"Email {user.email} was successfully verified.",
        "data": None
    }

    return return_value

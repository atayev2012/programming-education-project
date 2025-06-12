from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from config import config
import bcrypt
from fastapi.exceptions import HTTPException
from fastapi import status, Request, Response, Depends
from models import User
from database import SessionDep
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError


####### WORKING WITH PASSWORDS & TOKENS #########
# hashing password
def get_password_hash(password: str) -> str:
    encoded_pass = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(encoded_pass, salt)
    return hash.decode("utf-8")


# compare password with password hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    encoded_pass = plain_password.encode("utf-8")
    encoded_hash = hashed_password.encode("utf-8")
    return bcrypt.checkpw(encoded_pass, encoded_hash)


# create access/refresh token (data will contain only username)
def create_token(data: dict, type: str = "access"):
    if type not in ["access", "refresh"]:
        raise ValueError("type must be either 'access' or 'refresh'")

    exp_minutes = config.JWT_EXPIRATION_TIME if type == "access" else config.JWT_REFRESH_EXPIRATION_TIME * 24 * 60
    
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
########################################

######## UTILS AS DEPENDENCIES #########
# read token from cookies and get user
async def get_username_from_token(request: Request, response: Response) -> str | None:  
    # initialize http exception for invalid token
    unauthorized_err = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "success": False,
            "message": "Unauthorized access"
        }
        )
    # get access token from cookies
    access_token_from_cookie = request.cookies.get("access_token")
    
    # proceed with decoding access token if it exists
    try:
        if access_token_from_cookie is None:
            # raise error of unauthorized access because no access token was found
            raise JWTError()

        access_token_credentials = jwt.decode(access_token_from_cookie, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        return access_token_credentials["username"]
    
    except (ExpiredSignatureError, JWTError):
        # if access token is expired or invalid, then check for refresh token
        refresh_token_from_cookies = request.cookies.get("refresh_token")
        if refresh_token_from_cookies is None:
             # raise error of unauthorized access because no refresh token was found
             raise unauthorized_err
        
        # decode refresh token if exists
        try:
            refresh_token_credentials = jwt.decode(refresh_token_from_cookies, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
            # if refresh token is valid, then generate new access token and refresh tokens for the username
            # new access and refresh tokens
            data = {
            "username": refresh_token_credentials["username"]
            }
            response.set_cookie(
                key="access_token", 
                value=create_token(data), 
                httponly=True,  # Makes the cookie HTTP-only
                secure=True,  # Use secure flag for HTTPS connections
                max_age=timedelta(minutes=config.JWT_EXPIRATION_TIME),  # Expiration time
                expires=datetime.now(timezone.utc) + timedelta(minutes=config.JWT_EXPIRATION_TIME)  # Cookie expiration
            )

            response.set_cookie(
                key="refresh_token", 
                value=create_token(data, type="refresh"), 
                httponly=True,  # Makes the cookie HTTP-only
                secure=True,  # Use secure flag for HTTPS connections
                max_age=timedelta(days=config.JWT_REFRESH_EXPIRATION_TIME),  # Expiration time
                expires=datetime.now(timezone.utc) + timedelta(days=config.JWT_REFRESH_EXPIRATION_TIME)  # Cookie expiration
            )

            return refresh_token_credentials["username"]
          
        except (ExpiredSignatureError, JWTError) as e:
            # if refresh token is expired or invalid, then raise error of unauthorized access
            print(e)
            raise unauthorized_err
########################################


####### WORKING WITH USER FROM DATABASE ###########
async def get_user_by_username(session: SessionDep, username: str | None = Depends(get_username_from_token)):
    statement = select(User).filter(User.username == username)
    try:
        exec_result = await session.execute(statement)
        return exec_result.scalar_one_or_none()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "success": False,
                "message": "Server internal error occured. Try again later."
            })
###################################################
    

if __name__ == "__main__":
    pass
    password = "dpFA8UTsg!"
    data = {"name": "Batyr", "last_name": "Atayev", "username": "atayev2012@gmail.com"}
    password_hash = get_password_hash(password=password)
    print(f"Pass hash: {password_hash}")
    # print()
    # print(f"Password: {password + "i"} + hash: {password_hash}\nresult matching=> {verify_password(password, password_hash)}")
    # token = create_access_token(data, "refresh")
    # print()
    # print(token)
    # print()
    # print(get_current_username(token))



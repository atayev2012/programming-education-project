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

import smtplib
from email.mime.text import MIMEText


####### WORKING WITH PASSWORDS & TOKENS #########
# hashing password
def get_password_hash(password: str) -> str:
    '''Input plain password and receive hash as string

    Args:
        password (str): Plain password

    Returns:
        str: Hash of a plain password 
    '''
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
def create_token(data: dict, type: str = "access", secret_key: str = config.JWT_SECRET_KEY) -> str:
    if type not in ["access", "refresh"]:
        raise ValueError("type must be either 'access' or 'refresh'")

    exp_minutes = config.JWT_EXPIRATION_TIME if type == "access" else config.JWT_REFRESH_EXPIRATION_TIME * 24 * 60
    
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=config.JWT_ALGORITHM)
########################################

######## UTILS AS DEPENDENCIES #########
# just get username
async def get_username(token: str, secret_key = config.JWT_SECRET_KEY) -> str | None:
    # proceed with decoding access token if it exists
    invalid_err = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "success": False,
            "message": "Token is invalid"
        }
        )

    try:
        if token is None:
            # raise error of unauthorized access because no access token was found
            raise JWTError()
    
        token_credentials = jwt.decode(token, secret_key, algorithms=[config.JWT_ALGORITHM])
        return token_credentials["username"]
    except (ExpiredSignatureError, JWTError):
        raise invalid_err


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

async def set_token_to_cookies(token: str, type: str, response: Response) -> None:
    '''
    Args:
    token (str): token
    type (str): access or refresh
    response (fastapi.Response): response where cookie should be set

    Returns:
    None
    '''
    if type not in ["access", "refresh"]:
        raise ValueError("type must be either 'access' or 'refresh'")

    exp_minutes = config.JWT_EXPIRATION_TIME if type == "access" else config.JWT_REFRESH_EXPIRATION_TIME * 24 * 60

    response.set_cookie(
                key=type + "_token", 
                value=token, 
                httponly=True,  # Makes the cookie HTTP-only
                secure=True,  # Use secure flag for HTTPS connections
                max_age=timedelta(minutes=exp_minutes),  # Expiration time
                expires=datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)  # Cookie expiration
            )

########################################


####### WORKING WITH USER FROM DATABASE ###########
# find user by user name
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

# find user by filter
async def find_user_by_filter(filter_by,  session: SessionDep) -> User | None:
    statement = select(User).filter_by(**filter_by)
    data = await session.execute(statement)
    user = data.scalar_one_or_none()
    return user
###################################################
    

####### EMAIL VERIFICATION ##########
async def send_email_verification_token(user: User):    
    email_verification_token = create_token(
        {"username": user.username},
        secret_key=config.EMAIL_VERIFICATION_SECRET_KEY
    )

    link_to_send = config.WEB_APP_DOMAIN + f"/api/auth/email-verify/{email_verification_token}"


    msg = MIMEText(f"Hello, {User.first_name}\n\nYour verification link is {link_to_send}") 
    msg["Subject"] = "Testing email"
    msg["From"] = config.EMAIL
    msg["To"] = user.email

    with smtplib.SMTP_SSL(config.EMAIL_SMTP_SERVER, config.EMAIL_SMTP_SERVER_PORT) as smtp_server:
        # Login to the SMTP server using the sender's credentials.

        smtp_server.login(config.EMAIL, config.EMAIL_PASS)
        # Send the email. The sendmail function requires the sender's email, the list of recipients, and the email message as a string.
        smtp_server.sendmail(config.EMAIL, user.email, msg.as_string())
    # Print a message to console after successfully sending the email.
    print("Message sent!")

#####################################


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



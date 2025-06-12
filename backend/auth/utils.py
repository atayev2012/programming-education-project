# import sys
# import os
# import time

# parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# sys.path.append(parent_dir)

from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from config import config
import bcrypt
from fastapi.exceptions import HTTPException
from fastapi import status, Request, Response

# working with passwords
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


# create access/refresh token (data will contain username)
def create_token(data: dict, type: str = "access"):
    if type not in ["access", "refresh"]:
        raise ValueError("type must be either 'access' or 'refresh'")

    exp_minutes = config.JWT_EXPIRATION_TIME if type == "access" else 1 #config.JWT_REFRESH_EXPIRATION_TIME * 24 * 60
    
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

# decode token
def decode_token(token: str):
    try:
        return jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


######## UTILS AS DEPENDENCIES #########
# read token from cookies
def get_token_from_cookies(request: Request, response: Response) -> str | None:
    
    if access_token_from_cookie := request.cookies.get("access_token") is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")
    
    try:
        jwt.decode(access_token_from_cookie, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    except ExpiredSignatureError:
        if refresh_token_from_cookies := request.cookies.get("refresh_token") is None:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")

########################################

def get_current_username(token:str):
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)
    if not payload.get("username"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    return payload.get("username")
    

    


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



from pydantic import BaseModel, Field, EmailStr
from datetime import date

class UserSignUp(BaseModel):
    username: str = Field(max_length=50, description="unique username", examples=["nerd1995"])
    email: EmailStr = Field(max_length=100, description="user email address", examples=["test@mail.ru"])
    phone: str = Field(description="phone number with country code", examples=["79999999999"])
    first_name: str = Field(max_length=50, description="first name", examples=["George"])
    last_name: str = Field(max_length=50, description="last name", examples=["Washington"])
    middle_name: str | None = Field(max_length=50, description="optional - middle name")
    date_of_birth: date = Field(description="date of birth in format YYYY-MM-DD", examples=["2000-02-18"])
    gender: bool = Field(description="gender - True = male; False = female", examples=[True])
    password: str = Field(max_length=255, description="password", examples=["password"])


class BaseUser(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: str | None
    date_of_birth: date
    gender: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str


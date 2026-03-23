from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# This is the JSON format for Users
class UserBase(BaseModel):
    full_name: str = Field(min_length=5, max_length=200)
    username: str = Field(min_length=10, max_length=50)
    email: str = Field(min_length=20, max_length=120)

class UserCreate(UserBase):
    password: str = Field(min_length=10)

class UserUpdate(UserBase):
    full_name: str = Field(min_length=5, max_length=200)
    username: str = Field(min_length=10, max_length=50)
    email: str = Field(min_length=20, max_length=120)
    password: str = Field(min_length=10)

# class UserPublicResponse(BaseModel):

# class UserPrivateResponse(BaseModel):

# This is the JSON format for tokens (JWT)
class Token(BaseModel):
    access_token: str
    token_type: str




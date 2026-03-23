from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# This holds the JSON response format (how the backend retrieves and sends data)
class UserBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(min_length=6, max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=10)


class UserUpdate(BaseModel):
    full_name: str | None = Field(min_length=1, max_length=200)
    username: str | None = Field(min_length=1, max_length=50)
    email: EmailStr | None = Field(min_length=6, max_length=120)
    password: str | None = Field(min_length=10)


class UserPrivate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    email: EmailStr
    image_path: str

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_path: str

# This is the JSON format for tokens (JWT)
class Token(BaseModel):
    access_token: str
    token_type: str




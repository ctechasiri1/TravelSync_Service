from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime

# ==========================================
# DOMAIN: USERS
# ==========================================

class UserBase(BaseModel):
    """Shared properties used across multiple User validation schemas"""
    full_name: str = Field(min_length=1, max_length=200)
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(min_length=6, max_length=120)


class UserCreate(UserBase):
    """
    The Request Body expected from the iOS client to register a new account.
    Inherits base fields and strictly requires a raw password.
    """
    password: str = Field(min_length=3)


class UserUpdate(BaseModel):
    """
    The Request Body expected for updating an existing profile.
    All fields are optional to allow for partial updates from the client.
    """
    full_name: str | None = Field(min_length=1, max_length=200)
    username: str | None = Field(min_length=1, max_length=50)
    email: EmailStr | None = Field(min_length=6, max_length=120)
    password: str | None = Field(min_length=10)


class UserPrivate(BaseModel):
    """
    The secure Response Body sent when a user views their OWN profile.
    All fields are optional to alow for partial updates from the client.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    email: EmailStr
    image_path: str


class UserPublic(BaseModel):
    """
    The secure Response Body sent when viewing ANOTHER user's profile.
    Strictly limits PII (Personally Identifiable Information) like email.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_path: str

# ==========================================
# DOMAIN: AUTHENTICATION
# ==========================================

class Token(BaseModel):
    """Standard OAuth2 JSON response payload containing the JWT."""
    access_token: str
    token_type: str

# ==========================================
# DOMAIN: TRIPS
# ==========================================


class TripBase(BaseModel):
    """Shared properties used across multiple Trip validation schemas"""
    title: str = Field(min_length=1, max_length=200)
    location: str = Field(min_length=1, max_length=200)
    start_date: datetime
    end_date: datetime
    budget: float | None = Field(default=None, ge=0)
    cover_image: str | None = Field(default=None, max_length=200)


class TripCreate(TripBase):
    """The Request Body expected from the iOS client to create a new Trip."""
    pass


class TripPublic(TripBase):
    """The Response Body sent when viewing a Trip. Excludes sensitive fields."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int

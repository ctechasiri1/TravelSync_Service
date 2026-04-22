from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ==========================================
# DOMAIN: AUTHENTICATION
# ==========================================


class Token(BaseModel):
    """Standard OAuth2 JSON response payload containing the JWT."""

    access_token: str
    token_type: str


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

    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, min_length=6, max_length=120)


class UserPrivateResponse(BaseModel):
    """
    The secure Response Body sent when a user views their OWN profile.
    All fields are optional to alow for partial updates from the client.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    email: EmailStr
    profile_image_url: str


# ==========================================
# DOMAIN: TRIPS
# ==========================================


class TripBase(BaseModel):
    """Shared properties used across multiple Trip validation schemas"""

    title: str = Field(min_length=1, max_length=200)
    location: str = Field(min_length=1, max_length=200)
    start_date: datetime
    end_date: datetime
    budget: int
    is_favorite: bool


class TripCreate(TripBase):
    """The Request Body expected from the iOS client to create a new Trip."""


class TripUpdate(BaseModel):
    """Used for PATCH requests. All fields are optional."""

    is_favorite: bool | None = None


class TripPrivateResponse(TripBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    cover_image_url: str
    total_spending: int


# ==========================================
# DOMAIN: EXPENSE
# ==========================================


class ExpenseBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    amount: int = Field(ge=0)
    transaction_date: datetime
    category_id: int


class ExpenseCreate(ExpenseBase):
    trip_id: int
    receipt_image_data: str | None = None


class ExpensePrivateResponse(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int
    receipt_image_url: str | None = None

from typing import Annotated

from fastapi import Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from repositories.user_repository import UserRepository
from repositories.trip_repository import TripRepository
from services.user_service import UserService
from services.trip_service import TripService

from auth import oauth2_scheme, verify_access_token


# ==========================================
# USER INJECTION
# ==========================================

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)

# ==========================================
# TRIP INJECTION
# ==========================================

def get_trip_repository(db: AsyncSession = Depends(get_db)) -> TripRepository:
    return TripRepository(db)

def get_trip_service(repo: TripRepository = Depends(get_trip_repository)) -> TripService:
    return TripService(repo)

# ==========================================
# AUTHENTICATION INJECTION
# ==========================================

async def get_current_user(
        # 1. Extracts the Bearer token from the incoming HTTP Authorization header.
        token: Annotated[str, Depends(oauth2_scheme)],
        user_repo: UserRepository = Depends(get_user_repository)
) -> models.User:
    """
    FastAPI Dependency that protect secure endpoints.
    """
    # 2. Validates the token cryptographically
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = await user_repo.get_user_from_id(user_id_int)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW_Authenticate": "Bearer"}
        )
    
    # 4. Returns the full User object to the endpoint
    return user


# Endpoints can simply use 'user: CurrentUser' to securely require authentication.
CurrentUser = Annotated[models.User, Depends(get_current_user)]
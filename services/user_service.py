
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from services.auth import (
    create_access_token, 
    hash_password, 
    verify_password
)
from config import settings
from database import get_db
from schemas import UserCreate, UserPrivate, UserPublic, UserUpdate, Token
from typing_extensions import Annotated

from schemas import UserCreate


class UserService:
    """
    Service class for user-related operations.
    """
    async def create_user(self, user: UserCreate, db: AsyncSession):
        result = await db.execute(
            select(models.User)
            .where(func.lower(models.User.username) == user.username.lower())
        )

        existing_user = result.scalars().first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
    
        result = await db.execute(
            select(models.User)
            .where(func.lower(models.User.email) == user.email.lower())
        )

        existing_email = result.scalars().first()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
        new_user = models.User(
            username=user.username,
            full_name=user.full_name,
            email=user.email.lower(),
            password_hash=hash_password(user.password)
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user



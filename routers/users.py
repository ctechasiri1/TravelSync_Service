from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from config import settings
from database import get_db
from schemas import UserCreate, UserPrivate, UserPublic, UserUpdate, Token
from services.user_service import UserService
from exceptions import UserLoginError

router = APIRouter()

user_service = UserService()

@router.post("", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        new_user = await user_service.create_user(user, db)
        return new_user
    except UserLoginError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        token = await user_service.login_for_access_token(form_data, db)
        return token
    except UserLoginError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error)
        )
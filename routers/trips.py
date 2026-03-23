from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from schemas import UserCreate, UserPrivateResponse, UserPublicResponse, UserUpdate

router = APIRouter()

@router.get("", response_model=UserPri)
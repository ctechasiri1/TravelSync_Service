from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from services.auth import (
    get_current_user, 
)
from config import settings
from database import get_db
from schemas import UserCreate, UserPrivate, UserPublic, UserUpdate, Token, TripBase, TripCreate
from services.trip_service import TripService


router = APIRouter()

trip_service = TripService()

@router.post("", response_model=TripBase, status_code=status.HTTP_201_CREATED)
async def create_trip(trip: TripCreate, db: Annotated[AsyncSession, Depends(get_db)], current_user_id: Annotated[int, Depends(get_current_user)]):
    return await trip_service.create_trip(trip, db, current_user_id)






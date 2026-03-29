from typing import Annotated

from fastapi import APIRouter, Depends, status

from schemas import TripResponse, TripCreate
from services.trip_service import TripService
from dependencies import get_trip_service


router = APIRouter()


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(trip: TripCreate, service: TripService = Depends(get_trip_service)):
    return await service.create_trip(trip)







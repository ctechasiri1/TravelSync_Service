from datetime import datetime

from fastapi import APIRouter, Depends, status, Form, File, UploadFile, HTTPException

from schemas import TripPrivateResponse, TripCreate
from services.trip_service import TripService
from dependencies import get_trip_service, CurrentUser


router = APIRouter()


@router.post("", response_model=TripPrivateResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    current_user: CurrentUser,
    title: str = Form(...),
    location: str = Form(...),
    start_date: datetime = Form(...),
    end_date: datetime = Form(...),
    budget: int | None = Form(None),
    cover_image_file: UploadFile | None = File(None),
    service: TripService = Depends(get_trip_service)
    ):

    trip_data = TripCreate(
        title=title,
        location=location,
        start_date=start_date,
        end_date=end_date,
        budget=budget,
        cover_image=None
    )

    try:
        return await service.create_trip(trip_data, cover_image_file, current_user.id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
    

@router.get("", response_model=list[TripPrivateResponse])
async def get_trips(current_user: CurrentUser, service: TripService = Depends(get_trip_service)):
    return await service.get_trips(current_user.id)
    







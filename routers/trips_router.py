from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from dependencies import CurrentUser, get_trip_service
from exceptions import TripError
from schemas import TripCreate, TripPrivateResponse, TripUpdate
from services.trip_service import TripService

router = APIRouter()


@router.post(
    "", response_model=TripPrivateResponse, status_code=status.HTTP_201_CREATED
)
async def create_trip(
    current_user: CurrentUser,
    title: str = Form(...),
    location: str = Form(...),
    start_date: datetime = Form(...),
    end_date: datetime = Form(...),
    budget: int | None = Form(None),
    cover_image_file: UploadFile | None = File(None),
    service: TripService = Depends(get_trip_service),
):

    trip_data = TripCreate(
        title=title,
        location=location,
        start_date=start_date,
        end_date=end_date,
        budget=budget,
        cover_image=None,
    )

    try:
        return await service.create_trip(trip_data, cover_image_file, current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get(
    "", response_model=list[TripPrivateResponse], status_code=status.HTTP_200_OK
)
async def get_trips(
    current_user: CurrentUser, service: TripService = Depends(get_trip_service)
):
    return await service.get_trips(current_user.id)


@router.patch(
    "/{trip_id}", response_model=TripPrivateResponse, status_code=status.HTTP_200_OK
)
async def update_trip(
    trip_id: int,
    trip_data: TripUpdate,
    current_user: CurrentUser,
    service: TripService = Depends(get_trip_service),
):
    try:
        return await service.update_trip(trip_id, current_user.id, trip_data)
    except TripError as errror:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=errror)

from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from dependencies import CurrentUser, get_trip_service, get_exepense_service
from exceptions import TripError
from schemas import (
    TripCreate,
    TripPrivateResponse,
    TripUpdate,
    ExpensePrivateResponse,
    ExpenseCreate,
)
from services.trip_service import TripService
from services.expense_service import ExpenseService
from exceptions import UserError

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
    budget: int = Form(...),
    is_favorite: bool = Form(False),
    cover_image_file: UploadFile | None = File(None),
    service: TripService = Depends(get_trip_service),
):
    trip_data = TripCreate(
        title=title,
        location=location,
        start_date=start_date,
        end_date=end_date,
        budget=budget,
        is_favorite=is_favorite,
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
    current_user: CurrentUser,
    trip_id: int,
    is_favorite: bool | None = Form(None),
    cover_image_file: UploadFile | None = Form(None),
    service: TripService = Depends(get_trip_service),
):
    updated_trip = TripUpdate(is_favorite=is_favorite)

    try:
        return await service.update_trip(
            user_id=current_user.id,
            trip_id=trip_id,
            updates=updated_trip,
            cover_image_file=cover_image_file,
        )
    except TripError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    current_user: CurrentUser,
    trip_id: int,
    service: TripService = Depends(get_trip_service),
):
    try:
        await service.delete_trip(current_user.id, trip_id)
    except TripError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.post(
    "/{trip_id}/expense",
    response_model=ExpensePrivateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_expense(
    current_user: CurrentUser,
    trip_id: int,
    title: str = Form(...),
    amount: int = Form(...),
    transaction_date: datetime = Form(...),
    category_id: int = Form(...),
    receipt_image_file: UploadFile | None = Form(None),
    trip_service: TripService = Depends(get_trip_service),
    expense_service: ExpenseService = Depends(get_exepense_service),
):
    expense_data = ExpenseCreate(
        title=title,
        amount=amount,
        transaction_date=transaction_date,
        category_id=category_id,
        trip_id=trip_id,
    )
    try:
        await trip_service.verify_membership(current_user.id, trip_id)

        return await expense_service.create_expense(
            trip_id=trip_id,
            receipt_image_file=receipt_image_file,
            expense_data=expense_data,
        )
    except TripError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.get("/{trip_id}/expense", response_model=list[ExpensePrivateResponse], status_code=status.HTTP_200_OK)
async def get_expenses(
    current_user: CurrentUser,
    trip_id: int, 
    service: ExpenseService = Depends(get_exepense_service)
):
    try:
        return await service.get_expenses(user_id=current_user.id, trip_id=trip_id)
    except UserError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    
@router.delete("\{trip_id}\expenses", response_model=ExpensePrivateResponse, status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    current_user: CurrentUser,
    trip_id: int,
    service: ExpenseService = Depends(get_exepense_service)
):
    pass
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from dependencies import CurrentUser, get_exepense_service
from schemas import ExpenseCreate, ExpensePrivateResponse
from services.expense_service import ExpenseService

router = APIRouter()


@router.post("", response_model=ExpensePrivateResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    current_user: CurrentUser,
    title: str = Form(...),
    amount: int = Form(...),
    transaction_date: datetime = Form(...),
    category_id: int = Form(...),
    trip_id: int = Form(...),
    receipt_image: UploadFile | None = Form(None)
):
    pass

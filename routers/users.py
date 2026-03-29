from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth import CurrentUser
from dependencies import get_user_service
from schemas import UserCreate, UserPrivate, UserPublic, UserUpdate, Token
from services.user_service import UserService
from exceptions import UserLoginError

router = APIRouter()

@router.post("", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    try:
        return await service.valid_new_user(user)
    except UserLoginError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
    

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], service: UserService = Depends(get_user_service)):
    try:
        return await service.create_access_token(form_data)
    except UserLoginError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error)
        )
    
@router.get("/me", response_model=UserPrivate)
async def get_current_user(current_user: CurrentUser):
    return current_user


@router.get("{user_id}", response_model=UserPublic)
async def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    try:
        return await service.valid_user(user_id)
    except UserLoginError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
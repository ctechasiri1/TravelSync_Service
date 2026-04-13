from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm

import models
from auth import create_access_token, hash_password, verify_password
from config import settings
from exceptions import UserLoginError
from repositories.user_repository import UserRepository
from schemas import Token, UserCreate


class UserService:
    """Service class for user-related operations."""

    def __init__(self, user_repo: UserRepository):
        self.repo = user_repo

    async def valid_new_user(self, user: UserCreate) -> models.User:
        existing_user = await self.repo.get_user_from_email_and_username(
            user.email, user.username
        )

        if existing_user:
            if existing_user.username.lower() == user.username.lower():
                raise UserLoginError("The username already exists")

            if existing_user.email.lower() == user.email.lower():
                raise UserLoginError("The email already exists")

        new_user = models.User(
            username=user.username,
            full_name=user.full_name,
            email=user.email.lower(),
            password_hash=hash_password(user.password),
        )

        return await self.repo.add_and_save_user(new_user)

    async def valid_user(self, user_id: int) -> models.User:
        user = await self.repo.get_user_from_id(user_id)

        if user:
            return user

        raise UserLoginError("User not found.")

    async def create_access_token(self, form_data: OAuth2PasswordRequestForm) -> Token:
        existing_user = await self.repo.get_user_from_email(form_data.username)

        # verify the uesr exists and the password is correct
        if not existing_user or not verify_password(
            form_data.password, existing_user.password_hash
        ):
            raise UserLoginError("Incorrect email or password")

        # create an access token with the user id as the subject
        access_token_expire = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(existing_user.id)}, expires_delta=access_token_expire
        )

        return Token(access_token=access_token, token_type="bearer")

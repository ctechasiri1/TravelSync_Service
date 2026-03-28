
from datetime import timedelta

from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.security import OAuth2PasswordRequestForm

import models
from auth import (
    verify_password,
    hash_password, 
    create_access_token
)
from config import settings
from exceptions import UserLoginError
from schemas import UserCreate, Token

class UserService:
    """Service class for user-related operations."""

    async def create_user(self, user: UserCreate, db: AsyncSession):
        """
        Creates a new user in the database after validating uniqueness.

        This method checks if the provided username or email already exists in the database
        (case-insensitive). If both are unique, it hashes the user's password and persists
        the new user record.

        Args:
            user (UserCreate): The data transfer object containing the new user's details 
                (username, full_name, email, and raw password).
            db (AsyncSession): The asynchronous database session.

        Returns:
            models.User: The newly created and committed user database instance.

        Raises:
            UserLoginError: If the requested username or email is already registered.
        """
        query = select(models.User).where(
            or_(
                func.lower(models.User.username) == user.username.lower(),
                func.lower(models.User.email) == user.email.lower()
            )
        )

        result = await db.execute(query)
        existing_user = result.scalars().first()

        if existing_user:
            if existing_user.username.lower() == user.username.lower():
                raise UserLoginError("The username already exists")

            if existing_user.email.lower() == user.email.lower():
                raise UserLoginError("The email already exists")
    
        new_user = models.User(
            username=user.username,
            full_name=user.full_name,
            email=user.email.lower(),
            password_hash=hash_password(user.password)
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user
    
    async def login_for_access_token(self, form_data: OAuth2PasswordRequestForm, db: AsyncSession):
        """
        Creates a new user in the database after validating uniqueness.

        This method checks if the provided username or email already exists in the database
        (case-insensitive). If both are unique, it hashes the user's password and persists
        the new user record.

        Args:
            user (UserCreate): The data transfer object containing the new user's details 
                (username, full_name, email, and raw password).
            db (AsyncSession): The asynchronous database session.

        Returns:
            models.User: The newly created and committed user database instance.

        Raises:
            UserLoginError: If the requested username or email is already registered.
        """
        query = select(models.User).where(func.lower(models.User.email) == form_data.username.lower())

        result = await db.execute(query)
        user = result.scalars().first()

        #verify the uesr exists and the password is correct
        if not user or not verify_password(form_data.password, user.password_hash):
            raise UserLoginError("Incorrect email or password")

        #create an access token with the user id as the subject
        access_token_expire = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expire
        )

        return Token(
            access_token=access_token,
            token_type="bearer"
    )

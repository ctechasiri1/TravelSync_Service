from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

import models


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_from_username(self, username: str) -> models.User | None:
        query = select(models.User).where(
            func.lower(models.User.username) == username.lower(),
        )

        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_user_from_email(self, email: str) -> models.User | None:
        query = select(models.User).where(
            func.lower(models.User.email) == email.lower()
        )

        result = await self.db.execute(query)

        return result.scalars().first()

    async def get_user_from_id(self, user_id: int) -> models.User | None:
        query = select(models.User).where(models.User.id == user_id)

        result = await self.db.execute(query)

        return result.scalars().first()

    async def add_and_save_user(self, user: models.User) -> models.User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

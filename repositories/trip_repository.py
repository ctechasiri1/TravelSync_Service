from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

import models
from schemas import TripCreate


class TripRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_trip(
        self, trip_data: TripCreate, cover_image_name: str | None, user_id: int
    ) -> models.Trip:
        new_trip = models.Trip(
            **trip_data.model_dump(),
            cover_image=cover_image_name,
            user_id=user_id,
        )

        self.db.add(new_trip)
        await self.db.commit()
        await self.db.refresh(new_trip)
        return new_trip

    async def get_trips(self, user_id: int) -> list[models.Trip]:
        query = select(models.Trip).where(models.Trip.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_trip_by_id_and_user(self, user_id: int, trip_id: int) -> models.Trip | None:
        query = select(models.Trip).where(
            models.Trip.id == trip_id, models.Trip.user_id == user_id
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete_trip(self, user_id: int, trip_id: int) -> str | None:
        delete_trip_query = (
            delete(models.Trip)
            .where(models.Trip.user_id == user_id, models.Trip.id == trip_id)
            .returning(models.Trip.cover_image)
        )

        result = await self.db.execute(delete_trip_query)
        return result.scalar_one_or_none()

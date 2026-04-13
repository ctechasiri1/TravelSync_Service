from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from schemas import TripCreate


class TripRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_trip(
        self, trip_data: TripCreate, cover_image: str | None, user_id: int
    ) -> models.Trip:
        new_trip = models.Trip(
            **trip_data.model_dump(exclude={"cover_iamge"}),
            cover_image=cover_image,
            user_id=user_id,
        )

        self.db.add(new_trip)
        await self.db.commit()
        await self.db.refresh(new_trip)
        return new_trip

    async def get_trips(self, user_id: int) -> models.Trip:
        query = select(models.Trip).where(models.Trip.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_trip_by_id_and_user(self, trip_id: int, user_id: int) -> models.Trip:
        query = select(models.Trip).where(
            models.Trip.id == trip_id, models.Trip.user_id == user_id
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def save_strip(self, db_trip: models.Trip) -> models.Trip:
        await self.db.commit()
        await self.db.refresh(db_trip)
        return db_trip

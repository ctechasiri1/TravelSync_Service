from sqlalchemy.ext.asyncio import AsyncSession

import models
from sqlalchemy import select


class TripRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_and_save_trip(self, new_trip: models.Trip) -> models.Trip:
        self.db.add(new_trip)
        await self.db.commit()
        await self.db.refresh(new_trip)

        return new_trip
    
    async def get_trips(self, user_id: int) -> models.Trip:
        query = select(models.Trip).where(models.Trip.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()


import models
from schemas import TripCreate
from sqlalchemy.ext.asyncio import AsyncSession



class TripService:
    """Service class to handle business logic related to Trips."""

    async def create_trip(self, trip: TripCreate, db: AsyncSession, current_user_id: models.User):
        new_trip = models.Trip(
            title=trip.title,
            location=trip.location,
            start_date=trip.start_date,
            end_date=trip.end_date,
            budget=trip.budget,
            user_id=current_user_id.id
        )
        db.add(new_trip)
        await db.commit()
        await db.refresh(new_trip)
        return new_trip





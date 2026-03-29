import models
from schemas import TripCreate

from repositories.trip_repository import TripRepository


class TripService:
    """Service class to handle business logic related to Trips."""
    def __init__(self, trip_repo: TripRepository):
        self.repo = trip_repo


    async def create_trip(self, trip: TripCreate):

        new_trip = models.Trip(
            title=trip.title,
            location=trip.location,
            start_date=trip.start_date,
            end_date=trip.end_date,
            budget=trip.budget,
            user_id=trip.id
        )

        return await self.repo.add_and_save_trip(new_trip)







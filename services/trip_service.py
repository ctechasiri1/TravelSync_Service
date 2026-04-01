import models
from schemas import TripCreate
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from repositories.trip_repository import TripRepository
from file_utils import process_image, ImageType


class TripService:
    """Service class to handle business logic related to Trips."""
    def __init__(self, trip_repo: TripRepository):
        self.repo = trip_repo


    async def create_trip(self, trip: TripCreate, cover_imge_file: UploadFile | None, user_id: int) -> models.Trip:
        processed_image = None

        if cover_imge_file:
            raw_bytes = await cover_imge_file.read()

            processed_image = await run_in_threadpool(process_image, raw_bytes, ImageType.COVER)

        new_trip = models.Trip(
            title=trip.title,
            location=trip.location,
            start_date=trip.start_date,
            end_date=trip.end_date,
            cover_image=processed_image,
            budget=trip.budget,
            user_id=user_id
        )

        return await self.repo.add_and_save_trip(new_trip)
    
    async def get_trips(self, user_id: int) -> models.Trip:
        return await self.repo.get_trips(user_id)







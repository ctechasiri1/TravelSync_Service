from fastapi import UploadFile

import models
from exceptions import TripError
from repositories.trip_repository import TripRepository
from schemas import TripCreate, TripUpdate
from services.local_media_service import ImageType, LocalMediaService


class TripService:
    """Service class to handle business logic related to Trips."""

    def __init__(self, trip_repo: TripRepository, media_service: LocalMediaService):
        self.repo = trip_repo
        self.media = media_service

    async def create_trip(
        self, trip: TripCreate, cover_imge_file: UploadFile | None, user_id: int
    ) -> models.Trip:
        processed_image_name = None

        if cover_imge_file:
            processed_image_name = await self.media.proces_image(
                cover_imge_file, ImageType.COVER
            )

        return await self.repo.create_trip(trip, processed_image_name, user_id)

    async def get_trips(self, user_id: int) -> list[models.Trip]:
        return await self.repo.get_trips(user_id)

    async def update_trip(
        self, trip_id: int, user_id: int, trip_update: TripUpdate
    ) -> models.Trip:
        db_trip = await self.repo.get_trip_by_id_and_user(trip_id, user_id)

        if not db_trip:
            raise TripError("Trip not found or unauthorized.")

        update_data = trip_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_trip, field, value)

        return await self.repo.save_strip(db_trip)

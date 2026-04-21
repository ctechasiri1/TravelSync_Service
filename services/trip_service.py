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
        self.media_service = media_service

    async def create_trip(
        self, trip: TripCreate, cover_image_file: UploadFile | None, user_id: int
    ) -> models.Trip:
        processed_image_name = None

        if cover_image_file:
            processed_image_name = await self.media_service.proces_image(
                cover_image_file, ImageType.COVER
            )

        return await self.repo.create_trip(trip, processed_image_name, user_id)

    async def get_trips(self, user_id: int) -> list[models.Trip]:
        return await self.repo.get_trips(user_id)

    async def update_trip(
        self, user_id: int, trip_id: int, is_favorite: bool | None = None, cover_image_file: UploadFile | None = None
    ) -> models.Trip:
        db_trip = await self.repo.get_trip_by_id_and_user(trip_id, user_id)

        if not db_trip:
            raise TripError("Trip not found or not authorized.")
        
        if is_favorite is not None:
            db_trip.is_favorite = is_favorite

        if cover_image_file:
            filename = await self.media.proces_image(
                cover_image_file, ImageType.COVER
            )
            db_trip.cover_image = filename

        return await self.repo.save_trip(db_trip)
    
    async def delete_trip(
        self, user_id: int, trip_id: int 
    ) -> models.Trip:
        db_trip = await self.repo.get_trip_by_id_and_user(trip_id, user_id)

        if not db_trip:
            raise TripError("Trip not found or not authorized.")
        
        return await self.repo.delete_trip(db_trip)
    

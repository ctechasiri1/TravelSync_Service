from fastapi import UploadFile

import models
from exceptions import TripError
from repositories.trip_repository import TripRepository
from repositories.expense_repository import ExpenseRepository
from schemas import TripCreate, TripUpdate, TripPrivateResponse
from services.local_media_service import ImageType, LocalMediaService


class TripService:
    """Service class to handle business logic related to Trips."""

    def __init__(
        self,
        trip_repo: TripRepository,
        expense_repo: ExpenseRepository,
        media_service: LocalMediaService,
    ):
        self.trip_repo = trip_repo
        self.expense_repo = expense_repo
        self.media_service = media_service


    async def create_trip(
        self, trip: TripCreate, cover_image_file: UploadFile | None, user_id: int
    ) -> TripPrivateResponse:
        processed_image_name = None

        if cover_image_file:
            processed_image_name = await self.media_service.proces_image(
                cover_image_file, ImageType.COVER
            )

        db_trip  = await self.trip_repo.create_trip(trip, processed_image_name, user_id)

        return TripPrivateResponse(
                title=db_trip.title,
                location=db_trip.location,
                start_date=db_trip.start_date,
                end_date=db_trip.end_date,
                budget=db_trip.budget,
                is_favorite=db_trip.is_favorite,
                id=db_trip.id,
                user_id=db_trip.user_id,
                cover_image_url=db_trip.cover_image_url,
                total_spending=0
        )


    async def get_trips(self, user_id: int) -> list[TripPrivateResponse]:
        trips = await self.trip_repo.get_trips(user_id)

        results = []
        for trip in trips:
            total_spend = await self.expense_repo.get_total_spent(trip.id)
            results.append(TripPrivateResponse(
                title=trip.title,
                location=trip.location,
                start_date=trip.start_date,
                end_date=trip.end_date,
                budget=trip.budget,
                is_favorite=trip.is_favorite,
                id=trip.id,
                user_id=trip.user_id,
                cover_image_url=trip.cover_image_url,
                total_spending=total_spend
            ))

        return results


    async def update_trip(
        self,
        user_id: int,
        trip_id: int,
        updates: TripUpdate,
        cover_image_file: UploadFile | None = None,
    ) -> TripPrivateResponse:
        db_trip = await self.trip_repo.get_trip_by_id_and_user(user_id, trip_id)

        if not db_trip:
            raise TripError("Trip not found or not authorized.")

        for field, value in updates.model_dump(exclude_none=True).items():
            setattr(db_trip, field, value)

        if cover_image_file:
            filename = await self.media.proces_image(cover_image_file, ImageType.COVER)
            db_trip.cover_image = filename

        db_trip = await self.trip_repo.save_trip(db_trip)

        return TripPrivateResponse(
            title=db_trip.title,
            location=db_trip.location,
            start_date=db_trip.start_date,
            end_date=db_trip.end_date,
            budget=db_trip.budget,
            is_favorite=db_trip.is_favorite,
            id=db_trip.id,
            user_id=db_trip.user_id,
            cover_image_url=db_trip.cover_image_url,
            total_spending=await self.expense_repo.get_total_spent(db_trip.id)
        )


    async def delete_trip(self, user_id: int, trip_id: int) -> models.Trip:
        db_trip = await self.trip_repo.get_trip_by_id_and_user(user_id, trip_id)

        if not db_trip:
            raise TripError("Trip not found or not authorized.")

        return await self.trip_repo.delete_trip(db_trip)


    async def verify_membership(self, user_id: int, trip_id: int) -> None:
        db_trip = await self.trip_repo.get_trip_by_id_and_user(user_id, trip_id)

        if not db_trip:
            raise TripError("Trip not found or not authorized.")

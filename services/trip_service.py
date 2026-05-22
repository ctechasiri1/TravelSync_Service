from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import TripError
from repositories.trip_repository import TripRepository
from repositories.expense_repository import ExpenseRepository
from schemas import TripCreate, TripUpdate, TripPrivateResponse
from services.local_media_service import ImageType, LocalMediaService


class TripService:
    """Service class to handle business logic related to Trips."""

    def __init__(
        self,
        db: AsyncSession,
        trip_repo: TripRepository,
        expense_repo: ExpenseRepository,
        media_service: LocalMediaService,
    ):
        self.db = db
        self.trip_repo = trip_repo
        self.expense_repo = expense_repo
        self.media_service = media_service

    async def verify_membership(self, user_id: int, trip_id: int) -> None:
        db_trip = await self.trip_repo.get_trip_by_id_and_user(user_id, trip_id)

        if not db_trip:
            raise TripError("Trip not found or not authorized.")

    async def create_trip(
        self, trip: TripCreate, cover_image_file: UploadFile | None, user_id: int
    ) -> TripPrivateResponse:
        cover_image_name = None
        optimized_bytes = None

        if cover_image_file:
            cover_image_name, optimized_bytes = await self.media_service.process_image(
                cover_image_file, ImageType.COVER
            )

        db_trip = await self.trip_repo.create_trip(
            trip_data=trip, cover_image_name=cover_image_name, user_id=user_id
        )

        if cover_image_name and optimized_bytes:
            await self.media_service.save_image_to_disk(
                filename=cover_image_name,
                content=optimized_bytes,
                image_type=ImageType.COVER,
            )

        await self.db.commit()
        await self.db.refresh(db_trip)

        return TripPrivateResponse(
            title=db_trip.title,
            location=db_trip.location,
            longitude=db_trip.longitude,
            latitude=db_trip.latitude,
            start_date=db_trip.start_date,
            end_date=db_trip.end_date,
            budget=db_trip.budget,
            is_favorite=db_trip.is_favorite,
            id=db_trip.id,
            user_id=db_trip.user_id,
            cover_image_url=db_trip.cover_image_url,
            total_spending=0,
        )

    async def get_trips(self, user_id: int) -> list[TripPrivateResponse]:
        trips = await self.trip_repo.get_trips(user_id)

        results = []
        for trip in trips:
            total_spend = await self.expense_repo.get_total_spent(trip.id)
            results.append(
                TripPrivateResponse(
                    title=trip.title,
                    location=trip.location,
                    longitude=trip.longitude,
                    latitude=trip.latitude,
                    start_date=trip.start_date,
                    end_date=trip.end_date,
                    budget=trip.budget,
                    is_favorite=trip.is_favorite,
                    id=trip.id,
                    user_id=trip.user_id,
                    cover_image_url=trip.cover_image_url,
                    total_spending=total_spend,
                )
            )

        return results
    
    async def get_trip(self, trip_id: int) -> TripPrivateResponse:
        trip = await self.trip_repo.get_trip(trip_id)
        total_spend = await self.expense_repo.get_total_spent(trip_id)
        
        return TripPrivateResponse(
            title=trip.title,
            location=trip.location,
            longitude=trip.longitude,
            latitude=trip.latitude,
            start_date=trip.start_date,
            end_date=trip.end_date,
            budget=trip.budget,
            is_favorite=trip.is_favorite,
            id=trip.id,
            user_id=trip.user_id,
            cover_image_url=trip.cover_image_url,
            total_spending=total_spend,
        )

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

        old_cover_image_name = db_trip.cover_image
        updated_cover_image_name = None
        optimized_bytes = None

        if cover_image_file:
            updated_cover_image_name, optimized_bytes = await self.media_service.process_image(
                cover_image_file, ImageType.COVER
            )
            db_trip.cover_image = updated_cover_image_name

        if updated_cover_image_name and optimized_bytes:
            await self.media_service.save_image_to_disk(
                updated_cover_image_name, optimized_bytes, ImageType.COVER
            )

        await self.db.commit()
        await self.db.refresh(db_trip)

        if updated_cover_image_name and optimized_bytes:
            await self.media_service.delete_image(old_cover_image_name, ImageType.COVER)

        return TripPrivateResponse(
            title=db_trip.title,
            location=db_trip.location,
            longitude=db_trip.longitude,
            latitude=db_trip.latitude,
            start_date=db_trip.start_date,
            end_date=db_trip.end_date,
            budget=db_trip.budget,
            is_favorite=db_trip.is_favorite,
            id=db_trip.id,
            user_id=db_trip.user_id,
            cover_image_url=db_trip.cover_image_url,
            total_spending=await self.expense_repo.get_total_spent(db_trip.id),
        )

    async def delete_trip(self, user_id: int, trip_id: int) -> None:
        result = await self.trip_repo.delete_trip(user_id, trip_id)

        if result is None:
            raise TripError("The trip was not found or doesn't belong to this user.")
        
        _, trip_cover_image = result

        if trip_cover_image:
            await self.media_service.delete_image(trip_cover_image, ImageType.COVER)
        await self.db.commit()

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

import models
from repositories.expense_repository import ExpenseRepository
from schemas import ExpenseCreate
from services.local_media_service import ImageType, LocalMediaService
from services.trip_service import TripService
from exceptions import ExpenseError


class ExpenseService:
    def __init__(
        self,
        db: AsyncSession,
        repo: ExpenseRepository,
        trip_service: TripService,
        media_service: LocalMediaService,
    ):
        self.db = db
        self.repo = repo
        self.trip_service = trip_service
        self.media_service = media_service

    async def create_expense(
        self,
        user_id: int,
        trip_id: int,
        receipt_image_file: UploadFile | None,
        expense_data: ExpenseCreate,
    ) -> models.Expense:
        await self.trip_service.verify_membership(user_id, trip_id)

        receipt_image_name = None
        optimized_bytes = None

        if receipt_image_file:
            receipt_image_name, optimized_bytes = (
                await self.media_service.process_image(
                    receipt_image_file, ImageType.RECEIPT
                )
            )

        db_expense = await self.repo.create_expense(
            receipt_image_name=receipt_image_name, expense_data=expense_data
        )

        if receipt_image_name and optimized_bytes:
            await self.media_service.save_image_to_disk(
                receipt_image_name, optimized_bytes, ImageType.RECEIPT
            )

        await self.db.commit()
        await self.db.refresh(db_expense)

        return db_expense

    async def get_expenses(self, user_id: int, trip_id: int) -> list[models.Expense]:
        await self.trip_service.verify_membership(user_id, trip_id)
        return await self.repo.get_expenses(trip_id)

    async def delete_expense(self, user_id: int, trip_id: int, expense_id: int) -> None:
        await self.trip_service.verify_membership(user_id, trip_id)

        result = await self.repo.delete_expense(trip_id, expense_id)

        if result is None:
            raise ExpenseError(
                "The expense was not found or doesn't belong to this trip."
            )
        
        expense_id, receipt_image_name = result

        if receipt_image_name:
            await self.media_service.delete_image(receipt_image_name, ImageType.RECEIPT)
        await self.db.commit()
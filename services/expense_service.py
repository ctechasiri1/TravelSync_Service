from fastapi import UploadFile

import models
from repositories.expense_repository import ExpenseRepository
from schemas import ExpenseCreate
from services.local_media_service import ImageType, LocalMediaService


class ExpenseService:
    def __init__(self, repo: ExpenseRepository, media_service: LocalMediaService):
        self.repo = repo
        self.media_service = media_service

    async def create_expense(
        self,
        trip_id: int,
        receipt_image_file: UploadFile | None,
        expense_data: ExpenseCreate,
    ) -> models.Expense:
        processed_image = None

        if receipt_image_file:
            processed_image = await self.media_service.proces_image(
                receipt_image_file, ImageType.RECEIPT
            )

        return await self.repo.create_expense(
            trip_id=trip_id, receipt_image=processed_image, expense_data=expense_data
        )

from fastapi import UploadFile

import models
from repositories.expense_repository import ExpenseRepository
from schemas import ExpenseCreate
from services.local_media_service import ImageType, LocalMediaService

class ExpenseService:
    def __init__(self, repo: ExpenseRepository, media_service: LocalMediaService):
        self.repo = repo
        self.media_service = media_service
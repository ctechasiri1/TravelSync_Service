from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from schemas import ExpenseCreate

class ExpenseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
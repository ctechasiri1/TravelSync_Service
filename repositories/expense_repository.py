from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

import models
from schemas import ExpenseCreate


class ExpenseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_expense(
        self,
        trip_id: int,
        expense_data: ExpenseCreate,
        receipt_image: str | None = None,
    ) -> models.Expense:
        new_expense = models.Expense(
            **expense_data.model_dump(), receipt_image=receipt_image
        )
        self.db.add(new_expense)
        return await self.save_expense(new_expense)

    async def get_total_spent(self, trip_id: int) -> models.Expense:
        result = await self.db.execute(
            select(func.sum(models.Expense.amount)).where(models.Trip.id == trip_id)
        )

        return result.scalar() or 0

    async def save_expense(self, db_expense: models.Expense):
        await self.db.commit()
        await self.db.refresh(db_expense)
        return db_expense

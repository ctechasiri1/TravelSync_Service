from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

import models
from schemas import ExpenseCreate


class ExpenseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_expense(
        self,
        expense_data: ExpenseCreate,
        receipt_image_name: str | None = None,
    ) -> models.Expense:
        new_expense = models.Expense(
            **expense_data.model_dump(), receipt_image=receipt_image_name
        )

        self.db.add(new_expense)
        return new_expense

    async def get_total_spent(self, trip_id: int) -> int | float:
        query = select(func.sum(models.Expense.amount)).where(models.Trip.id == trip_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_expenses(self, trip_id) -> list[models.Expense]:
        query = select(models.Expense).where(models.Expense.trip_id == trip_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_expense(self, trip_id: int, expense_id: int) -> tuple[int, str] | None:
        delete_expense_query = (
            delete(models.Expense)
            .where(models.Expense.trip_id == trip_id, models.Expense.id == expense_id)
            .returning(models.Expense.id, models.Expense.receipt_image)
        )

        result = await self.db.execute(delete_expense_query)
        return result.first()
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from config import Settings

# ==========================================
# CORE USERS
# ==========================================


class User(Base):
    """
    Database model representing a registered account in TravelSync.

    Acts as the root node for all user-generated content.
    Includes cascading deletes: if a User is deleted, all associated Trips
    (and subsequently Events) are permanently removed from the database.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    profile_image: Mapped[str | None] = mapped_column(
        String(200), nullable=True, default=None
    )

    # creates relationship with a TRIP, a USER can have multiple TRIPs
    trips: Mapped[list[Trip]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    @property
    def profile_image_url(self) -> str:
        """
        Computed property that translates the raw database filename into a
        fully qualified static URL path for the iOS client to fetch
        """
        if self.profile_image:
            return f"{Settings.base_url}/media/profile_images/{self.profile_image}"
        return f"{Settings.base_url}/static/profile_image/default.png"


# ==========================================
# TRAVEL PLANNING
# ==========================================


class Trip(Base):
    """
    Database model representing a single travel itinerary.

    Owned exclusively by one User. Acts as the parent container for
    granular schedule items (Events).
    """

    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    cover_image: Mapped[str | None] = mapped_column(
        String(200), nullable=True, default=None
    )
    budget: Mapped[int] = mapped_column(Integer, nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # creates a relationship with the USER, a USER can have multiple TRIPS
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author: Mapped[User] = relationship(back_populates="trips")

    # creates a relationship with a EVENT, a TRIP can have multiple EVENTS
    events: Mapped[list[Event]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )

    expenses: Mapped[list[Expense]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )

    @property
    def cover_image_url(self) -> str:
        """
        Computed property that translates the raw database filename into a
        fully qualified static URL path for the iOS client to fetch
        """
        if self.cover_image:
            return f"{Settings.base_url}/media/cover_images/{self.cover_image}"
        return f"{Settings.base_url}/static/cover_image/default.png"


class Event(Base):
    """
    Database model representing a scheduled acitivity within a Trip.

    Relies entirely on the parent Trip. Cannot exist orphaned
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # creates a relationship with the TRIP, a TRIP can have multiple EVENTS
    trip_id: Mapped[int] = mapped_column(
        ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trip: Mapped[Trip] = relationship(back_populates="events")


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    receipt_image: Mapped[str | None] = mapped_column(
        String(200), nullable=True, default=None
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("expense_categories.id", ondelete="RESTRICT"), nullable=False
    )
    trip_id: Mapped[int] = mapped_column(
        ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True
    )

    category: Mapped["ExpenseCategory"] = relationship(back_populates="expenses")
    trip: Mapped[Trip] = relationship(back_populates="expenses")

    @property
    def receipt_image_url(self) -> str | None:
        if self.receipt_image:
            return f"{Settings.base_url}/media/documents/{self.receipt_image}"
        return None


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key_name: Mapped[str] = mapped_column(String(50), nullable=False)

    expenses: Mapped[list["Expense"]] = relationship(back_populates="category")

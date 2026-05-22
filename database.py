"""
Core database configuration and session management for TravelSync.

Initializes the async SQLAlchemy engine and provides the
dependency injection function required by FastAPI routers to securely
interact with the database.
"""

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# ==========================================
# DATABASE CONFIGURATION
# ==========================================

# The local SQLite databse file path
# (Note: This connection string will change when migrating to PostgreSQL)
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./travelsync.db"


# The core async engine that manges the physical connection pool to the db
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    # 'check_same_thread=False' is strictly required for SQLite to work with FastAPI async
    connect_args={"check_same_thread": False},
)


# REMOVE: This will be removed when we transfer to the PostgreSQL DB
# this enables the cascade delete based on the Foreign Key
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()

# A factory pattern that generates temporary, isolated database sessions.
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """
    The Foundational class that all SQLAlchemy models(User, Trip, etc.) must inherit from.
    Maintains the metadata catalog of all tables and relationships.
    """

    pass


# ==========================================
# DEPENDENCY INJECTION
# ==========================================


async def get_db():
    """
    FastAPI Dependdency that provides a secure, isolated database session per request.

    Yields the session to the endpoint for executing queries, and automatically
    closes the connection when the request finishes, preventing memory leaks.
    """
    async with AsyncSessionLocal() as session:
        yield session

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


# sqlite local database
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"


# this creates the ACTUAL database
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# this CREATES a database session to use and access
AsyncSessionLocal = async_sessionmaker (
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


# this is the function to run the connection/session to the database
async def get_db():
    async with AsyncSessionLocal() as session:
        # PAUSE this function and gives the database session to the endpoint to use
        yield session
    # the 'async with' block completes and automatically closes the connection


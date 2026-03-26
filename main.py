"""
Main application entry point for the TravelSync FastAPI backend.

This module initializes the ASGI application, configures the database
lifespan events, mounts static directories for media hosting, and
registers all API routers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import Base, engine

from routers import trips, users

# ==========================================
# APPLICATION LIFECYCLE
# ==========================================

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Manges the application lifecycle (startup and shutdown).

    Startup Phase (Before yield):
        Connects to the database engine and creates all tables defined
        in the SQLAlchmey metadata if they do not already exist.

    Shutdown Phase (After yield):
        Gracefully disposes of the database engine connection pool to
        prevent memory leaks when the sever stops.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


# ==========================================
# APP INITIALIZATION & CONFIGURATION
# ==========================================

app = FastAPI(lifespan=lifespan)

# Mount the local media directory to serve profile/cover pictures and documents
# (Note: This will be replaced by AWS S3 URLs in production)
app.mount("/media", StaticFiles(directory="media"), name="media")


# ==========================================
# ROUTER REGISTRATION
# ==========================================

app.include_router(users.router, prefix="/api/users", tags=["users"])


app.include_router(
    trips.router,
    prefix="/api/trips",  # Optional: Adds a common prefix to all routes in the router
    tags=["trips"]     # Optional: Groups these routes in the automatic documentation
)


from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import Base, engine

from routers import users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


# app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")


app.include_router(users.router, prefix="/api/users", tags=["users"])


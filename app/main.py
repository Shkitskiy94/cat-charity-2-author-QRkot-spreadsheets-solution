from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import settings
from app.core.init_db import create_first_superuser


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Это НЕОБЯЗАТЕЛЬНО.
    Материал про создание суперпользователя подаётся как бонус.
    Студенты могут на это забить.
    """
    await create_first_superuser()
    yield

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    lifespan=lifespan,  # может отсутствовать, это норм.
)
app.include_router(main_router)

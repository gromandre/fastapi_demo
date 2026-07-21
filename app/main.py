from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.exception_handlers import register_exception_handlers
from app.database.session import engine
from app.routers.documents import router as documents_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(lifespan=lifespan)
register_exception_handlers(app)
app.include_router(documents_router)

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DatabaseSettings

settings = DatabaseSettings.from_env()

DATABASE_URL = URL.create(
    "postgresql+psycopg",
    username=settings.user,
    password=settings.password,
    host=settings.host,
    port=settings.port,
    database=settings.name,
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

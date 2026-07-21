from minio import Minio

from app.core.config import MinioSettings

settings = MinioSettings.from_env()
MINIO_BUCKET = settings.bucket

minio_client = Minio(
    endpoint=settings.endpoint,
    access_key=settings.access_key,
    secret_key=settings.secret_key,
    secure=False,
)

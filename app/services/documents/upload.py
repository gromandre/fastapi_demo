from datetime import date
from typing import BinaryIO
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.database.models import Document
from app.integrations.minio import MINIO_BUCKET, minio_client
from app.schemas import DocumentUploadResponse
from app.services.documents.errors import (
    DocumentPersistenceError,
    EmptyDocumentError,
    StorageUnavailableError,
    UnsupportedDocumentTypeError,
)


def validate_png(
    *,
    filename: str | None,
    content_type: str | None,
    size: int | None,
) -> None:
    is_png = (
        content_type == "image/png"
        and filename is not None
        and filename.lower().endswith(".png")
    )
    if not is_png:
        raise UnsupportedDocumentTypeError("Image must have PNG format")

    if not size:
        raise EmptyDocumentError("File is empty")


class DocumentUploadService:
    async def upload(
        self,
        *,
        content: BinaryIO,
        filename: str | None,
        content_type: str | None,
        size: int | None,
        session: AsyncSession,
    ) -> DocumentUploadResponse:
        validate_png(filename=filename, content_type=content_type, size=size)
        object_name = f"{uuid4()}.png"

        try:
            await run_in_threadpool(
                minio_client.put_object,
                MINIO_BUCKET,
                object_name,
                content,
                size,
                content_type=content_type,
            )
        except Exception as exc:
            raise StorageUnavailableError("Object storage is unavailable") from exc

        try:
            document = Document(path=object_name, date=date.today())
            session.add(document)
            await session.commit()
            await session.refresh(document)
        except Exception as exc:
            await session.rollback()
            await _remove_uploaded_object(object_name)
            raise DocumentPersistenceError("Failed to save document") from exc

        return DocumentUploadResponse(
            id=document.id,
            path=document.path,
            date=document.date,
        )


async def _remove_uploaded_object(object_name: str) -> None:
    try:
        await run_in_threadpool(
            minio_client.remove_object,
            MINIO_BUCKET,
            object_name,
        )
    except Exception:
        # The original database error remains the primary failure.
        pass


document_upload_service = DocumentUploadService()

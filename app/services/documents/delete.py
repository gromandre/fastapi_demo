from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.database.models import Document
from app.integrations.minio import MINIO_BUCKET, minio_client
from app.schemas import DocumentDeleteResponse
from app.services.documents.errors import (
    DocumentNotFoundError,
    DocumentPersistenceError,
    StorageUnavailableError,
)


class DocumentDeleteService:
    async def delete(
        self,
        *,
        document_id: int,
        session: AsyncSession,
    ) -> DocumentDeleteResponse:
        document = await session.get(Document, document_id)
        if document is None:
            raise DocumentNotFoundError("Document not found")

        try:
            await run_in_threadpool(
                minio_client.remove_object,
                MINIO_BUCKET,
                document.path,
            )
        except Exception as exc:
            raise StorageUnavailableError("Object storage is unavailable") from exc

        try:
            await session.delete(document)
            await session.commit()
        except Exception as exc:
            await session.rollback()
            raise DocumentPersistenceError("Failed to delete document") from exc

        return DocumentDeleteResponse(
            id=document_id,
            msg="Document deleted",
        )


document_delete_service = DocumentDeleteService()

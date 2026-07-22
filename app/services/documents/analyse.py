from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.database.models import Document
from app.integrations.celery import celery_app
from app.schemas import DocumentAnalyseResponse
from app.services.documents.errors import (
    DocumentNotFoundError,
    TaskBrokerUnavailableError,
)


class DocumentAnalyseService:
    async def analyse(
        self,
        *,
        document_id: int,
        session: AsyncSession,
    ) -> DocumentAnalyseResponse:
        document = await session.get(Document, document_id)
        if document is None:
            raise DocumentNotFoundError("Document not found")

        try:
            task = await run_in_threadpool(
                celery_app.send_task,
                "analyse_document",
                args=[document_id],
            )
        except Exception as exc:
            raise TaskBrokerUnavailableError("Task broker is unavailable") from exc

        return DocumentAnalyseResponse(
            document_id=document_id,
            task_id=task.id,
            status="queued",
        )


document_analyse_service = DocumentAnalyseService()

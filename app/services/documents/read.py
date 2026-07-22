from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Document, DocumentText
from app.schemas import DocumentTextResponse
from app.services.documents.errors import (
    DocumentNotFoundError,
    DocumentTextNotFoundError,
)


class DocumentTextService:
    async def get_text(
        self,
        *,
        document_id: int,
        session: AsyncSession,
    ) -> DocumentTextResponse:
        document = await session.get(Document, document_id)
        if document is None:
            raise DocumentNotFoundError("Document not found")

        document_text = await session.scalar(
            select(DocumentText).where(DocumentText.id_doc == document_id)
        )
        if document_text is None:
            raise DocumentTextNotFoundError("Text not found")

        return DocumentTextResponse(
            document_id=document_id,
            text_id=document_text.id,
            text=document_text.text,
        )


document_text_service = DocumentTextService()

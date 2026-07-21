from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Document, DocumentText
from app.services.documents.errors import (
    DocumentNotFoundError,
    DocumentTextNotFoundError,
)


async def get_document_text(
    *,
    document_id: int,
    session: AsyncSession,
) -> DocumentText:
    document = await session.get(Document, document_id)
    if document is None:
        raise DocumentNotFoundError("Document not found")

    document_text = await session.scalar(
        select(DocumentText).where(DocumentText.id_doc == document_id)
    )
    if document_text is None:
        raise DocumentTextNotFoundError("Text not found")

    return document_text

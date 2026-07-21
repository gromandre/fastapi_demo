import io

import pytesseract
from PIL import Image
from sqlalchemy import select

from app.database.models import Document, DocumentText
from app.integrations.celery import celery_app
from app.integrations.minio import MINIO_BUCKET, minio_client
from worker.database import SessionLocal


@celery_app.task(name="analyse_document")
def analyse_document(document_id: int):
    with SessionLocal() as session:
        document = session.get(Document, document_id)

        if document is None:
            return {"status": "not_found", "document_id": document_id}

        response = minio_client.get_object(
            MINIO_BUCKET,
            document.path,
        )

        try:
            image_bytes = response.read()
        finally:
            response.close()
            response.release_conn()

        with Image.open(io.BytesIO(image_bytes)) as image:
            recognized_text = pytesseract.image_to_string(
                image,
                lang="rus+eng",
            )

        document_text = session.scalar(
            select(DocumentText).where(DocumentText.id_doc == document.id)
        )
        if document_text is None:
            document_text = DocumentText(
                id_doc=document.id,
                text=recognized_text,
            )
            session.add(document_text)
        else:
            document_text.text = recognized_text
        session.commit()

        return {
            "status": "completed",
            "document_id": document.id,
        }

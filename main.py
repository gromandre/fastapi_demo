from fastapi import FastAPI, UploadFile, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from uuid import uuid4
from starlette.concurrency import run_in_threadpool

from schemas import (
    DocumentTextResponse,
    DocumentAnalyseResponse,
    DocumentDeleteResponse,
    DocumentUploadResponse,
    ErrorResponse,
)
from storage import minio_client, MINIO_BUCKET
from datetime import date
from models import Document, DocumentText
from celery_app import celery_app

app = FastAPI()

@app.post(
    "/upload_doc",
    status_code=201,
    response_model=DocumentUploadResponse,
    summary="Загрузить документ",
    description=(
        "Принимает изображение в формате PNG, сохраняет его в MinIO "
        "и создаёт запись о документе в PostgreSQL."
    ),
    response_description="Созданный документ",
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Передан пустой файл",
        },
        415: {
            "model": ErrorResponse,
            "description": "Файл не является PNG-изображением",
        },
        500: {
            "model": ErrorResponse,
            "description": "Не удалось сохранить документ в базе данных",
        },
        503: {
            "model": ErrorResponse,
            "description": "Хранилище MinIO недоступно",
        },
    },
)

async def upload_doc(file: UploadFile, session: AsyncSession = Depends(get_db)):
    if file.content_type != "image/png" or not file.filename or not file.filename.lower().endswith(".png"):
        raise HTTPException(status_code=415, detail='image must have format .png')

    if not file.size:
        raise HTTPException(status_code=400, detail='file is empty')

    object_name = f"{uuid4()}.png"

    try:
        await run_in_threadpool(
            minio_client.put_object,
            MINIO_BUCKET,
            object_name,
            file.file,
            file.size,
            content_type=file.content_type
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Object storage is unavailable",
        ) from exc

    try:
        document = Document(path=object_name, date=date.today())
        session.add(document)
        await session.commit()

    except Exception:
        await session.rollback()

        await run_in_threadpool(
            minio_client.remove_object,
            MINIO_BUCKET,
            object_name,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to save document",
        )

    await session.refresh(document)
    return {
        "id": document.id,
        "path": document.path,
        "date": document.date,
    }


@app.delete(
    "/doc_delete/{document_id}",
    response_model=DocumentDeleteResponse,
    summary="Удалить документ",
    description=(
        "Удаляет изображение из MinIO и запись документа из PostgreSQL. "
        "Связанный распознанный текст удаляется каскадно."
    ),
    response_description="Результат удаления документа",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Документ с указанным id не найден",
        },
        500: {
            "model": ErrorResponse,
            "description": "Не удалось удалить документ из базы данных",
        },
        503: {
            "model": ErrorResponse,
            "description": "Хранилище MinIO недоступно",
        },
    },
)
async def doc_delete(document_id: int, session: AsyncSession = Depends(get_db)):
    document = await session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        await run_in_threadpool(
            minio_client.remove_object,
            MINIO_BUCKET,
            document.path,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Object storage is unavailable"
        ) from exc

    try:
        await session.delete(document)
        await session.commit()
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete document"
        ) from exc

    return {
        "id": document_id,
        "msg": "Document deleted"
    }

@app.post(
    "/doc_analyse/{document_id}",
    status_code=202,
    response_model=DocumentAnalyseResponse,
    summary="Запустить распознавание документа",
    description=(
        "Проверяет существование документа и отправляет Celery-задачу "
        "в RabbitMQ. Worker загружает изображение из MinIO, распознаёт "
        "текст через Tesseract и сохраняет результат в PostgreSQL."
    ),
    response_description="Задача поставлена в очередь",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Документ с указанным id не найден",
        },
        503: {
            "model": ErrorResponse,
            "description": "Брокер RabbitMQ недоступен",
        },
    },
)
async def analyse_document(
    document_id: int,
    session: AsyncSession = Depends(get_db),
):
    document = await session.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    try:
        task = await run_in_threadpool(
            celery_app.send_task,
            "analyse_document",
            args=[document_id],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Task broker is unavailable",
        ) from exc

    return {
        "document_id": document_id,
        "task_id": task.id,
        "status": "queued",
    }

@app.get(
    "/get_text/{document_id}",
    response_model=DocumentTextResponse,
    summary="Получить распознанный текст",
    description=(
        "Принимает id документа и возвращает сохранённый результат "
        "распознавания из таблицы documents_text."
    ),
    response_description="Распознанный текст документа",
    responses={
        404: {
            "model": ErrorResponse,
            "description": (
                "Документ не найден либо текст ещё не был распознан"
            ),
        },
    },
)
async def get_text(
    document_id: int,
    session: AsyncSession = Depends(get_db),
):
    document = await session.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    document_text = await session.scalar(
        select(DocumentText)
        .where(DocumentText.id_doc == document_id)
    )

    if document_text is None:
        raise HTTPException(
            status_code=404,
            detail="Text not found",
        )

    return {
        "document_id": document_id,
        "text_id": document_text.id,
        "text": document_text.text,
    }
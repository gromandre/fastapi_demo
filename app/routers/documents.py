from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas import (
    DocumentAnalyseResponse,
    DocumentDeleteResponse,
    DocumentTextResponse,
    DocumentUploadResponse,
    ErrorResponse,
)
from app.services.documents import (
    analyse_document,
    delete_document,
    get_document_text,
    upload_document,
)

router = APIRouter(tags=["documents"])
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/upload_doc",
    status_code=201,
    response_model=DocumentUploadResponse,
    summary="Загрузить документ",
    responses={
        400: {"model": ErrorResponse, "description": "Передан пустой файл"},
        415: {"model": ErrorResponse, "description": "Файл не является PNG"},
        500: {"model": ErrorResponse, "description": "Ошибка сохранения документа"},
        503: {"model": ErrorResponse, "description": "MinIO недоступен"},
    },
)
async def upload_doc(
    file: UploadFile,
    session: DatabaseSession,
):
    document = await upload_document(
        content=file.file,
        filename=file.filename,
        content_type=file.content_type,
        size=file.size,
        session=session,
    )
    return {
        "id": document.id,
        "path": document.path,
        "date": document.date,
    }


@router.delete(
    "/doc_delete/{document_id}",
    response_model=DocumentDeleteResponse,
    summary="Удалить документ",
    responses={
        404: {"model": ErrorResponse, "description": "Документ не найден"},
        500: {"model": ErrorResponse, "description": "Ошибка удаления документа"},
        503: {"model": ErrorResponse, "description": "MinIO недоступен"},
    },
)
async def doc_delete(
    document_id: int,
    session: DatabaseSession,
):
    await delete_document(document_id=document_id, session=session)
    return {"id": document_id, "msg": "Document deleted"}


@router.post(
    "/doc_analyse/{document_id}",
    status_code=202,
    response_model=DocumentAnalyseResponse,
    summary="Запустить распознавание документа",
    responses={
        404: {"model": ErrorResponse, "description": "Документ не найден"},
        503: {"model": ErrorResponse, "description": "RabbitMQ недоступен"},
    },
)
async def analyse_document_route(
    document_id: int,
    session: DatabaseSession,
):
    task_id = await analyse_document(
        document_id=document_id,
        session=session,
    )
    return {
        "document_id": document_id,
        "task_id": task_id,
        "status": "queued",
    }


@router.get(
    "/get_text/{document_id}",
    response_model=DocumentTextResponse,
    summary="Получить распознанный текст",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Документ или распознанный текст не найден",
        },
    },
)
async def get_text(
    document_id: int,
    session: DatabaseSession,
):
    document_text = await get_document_text(
        document_id=document_id,
        session=session,
    )
    return {
        "document_id": document_id,
        "text_id": document_text.id,
        "text": document_text.text,
    }

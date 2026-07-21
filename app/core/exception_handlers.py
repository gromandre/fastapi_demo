from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.services.documents.errors import (
    DocumentNotFoundError,
    DocumentPersistenceError,
    DocumentServiceError,
    DocumentTextNotFoundError,
    EmptyDocumentError,
    StorageUnavailableError,
    TaskBrokerUnavailableError,
    UnsupportedDocumentTypeError,
)

ERROR_STATUS_CODES: dict[type[DocumentServiceError], int] = {
    UnsupportedDocumentTypeError: 415,
    EmptyDocumentError: 400,
    DocumentNotFoundError: 404,
    DocumentTextNotFoundError: 404,
    StorageUnavailableError: 503,
    DocumentPersistenceError: 500,
    TaskBrokerUnavailableError: 503,
}


async def document_service_error_handler(
    _request: Request,
    exc: DocumentServiceError,
) -> JSONResponse:
    return JSONResponse(
        status_code=ERROR_STATUS_CODES.get(type(exc), 500),
        content={"detail": str(exc)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        DocumentServiceError,
        document_service_error_handler,
    )

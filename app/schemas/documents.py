from datetime import date

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    detail: str


class DocumentUploadResponse(BaseModel):
    id: int
    path: str
    date: date

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 4,
                "path": "40571313-d3d1-45b3-95a4-db0d17396b10.png",
                "date": "2026-07-17",
            }
        }
    )


class DocumentDeleteResponse(BaseModel):
    id: int
    msg: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 2,
                "msg": "Document deleted",
            }
        }
    )


class DocumentAnalyseResponse(BaseModel):
    document_id: int
    task_id: str
    status: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_id": 3,
                "task_id": "b82cf6b8-6927-4e85-90b3-cf749771db61",
                "status": "queued",
            }
        }
    )


class DocumentTextResponse(BaseModel):
    document_id: int
    text_id: int
    text: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_id": 3,
                "text_id": 1,
                "text": "Распознанный текст документа",
            }
        }
    )

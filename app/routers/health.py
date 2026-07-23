from fastapi import APIRouter

from app.schemas import CheckHealthResponse, ErrorResponse
from app.services import check_health_service

router = APIRouter(tags=["health"])


@router.get(
    "/healthcheck",
    status_code=200,
    response_model=CheckHealthResponse,
    summary="Проверить работу сервиса",
    responses={
        500: {"model": ErrorResponse, "description": "Сервис недоступен"},
    },
)
def check_service() -> CheckHealthResponse:
    return check_health_service.check()

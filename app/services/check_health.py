from app.schemas import CheckHealthResponse


class CheckHealthService:
    def check(self) -> CheckHealthResponse:
        return CheckHealthResponse(
            status=True,
        )


check_health_service = CheckHealthService()

from app.services.check_health import CheckHealthService


def test_health_service_returns_success():
    service = CheckHealthService()

    result = service.check()

    assert result.status is True
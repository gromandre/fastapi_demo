from pydantic import BaseModel, ConfigDict


class CheckHealthResponse(BaseModel):
    status: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": True,
            }
        }
    )
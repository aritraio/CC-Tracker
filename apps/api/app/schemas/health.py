from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    status: str = Field("healthy", description="Current service health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp of health check",
    )
    environment: str = Field(..., description="Runtime environment")

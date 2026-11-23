from fastapi import APIRouter
from pydantic import BaseModel

from service_monitor.core.config import settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    environment: str


@router.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok", environment=settings.environment)

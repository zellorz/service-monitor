from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CheckRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int
    checked_at: datetime
    is_up: bool
    status_code: int | None
    response_time_ms: int | None
    error: str | None
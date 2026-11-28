from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from service_monitor.core.db import Base


class Check(Base):
    __tablename__ = "checks"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), index=True
    )
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    is_up: Mapped[bool]
    status_code: Mapped[int | None]  # None si ni siquiera respondió
    response_time_ms: Mapped[int | None]
    error: Mapped[str | None] = mapped_column(String(500))  # motivo del fallo, si lo hay
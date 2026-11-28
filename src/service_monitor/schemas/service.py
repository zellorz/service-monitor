from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ServiceBase(BaseModel):
    """Campos comunes a crear y leer."""

    name: str = Field(min_length=1, max_length=100)
    url: HttpUrl  # Pydantic valida que sea una URL http(s) correcta
    interval_minutes: int = Field(default=5, ge=1, le=1440)  # entre 1 min y 1 día
    is_active: bool = True


class ServiceCreate(ServiceBase):
    """Lo que el cliente envía para crear un servicio."""


class ServiceUpdate(BaseModel):
    """Lo que el cliente envía para modificar: todo opcional."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    url: HttpUrl | None = None
    interval_minutes: int | None = Field(default=None, ge=1, le=1440)
    is_active: bool | None = None


class ServiceRead(ServiceBase):
    """Lo que la API devuelve."""

    model_config = ConfigDict(from_attributes=True)  # permite construirlo desde modelo SQLAlchemy

    id: int
    created_at: datetime
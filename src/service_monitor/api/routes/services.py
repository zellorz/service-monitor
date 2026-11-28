from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from service_monitor.core.db import get_db
from service_monitor.models import Check, Service
from service_monitor.monitoring.checker import run_check
from service_monitor.schemas.check import CheckRead
from service_monitor.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate

router = APIRouter(prefix="/services", tags=["services"])

DbSession = Annotated[Session, Depends(get_db)]  # alias para no repetirlo en cada endpoint


def get_service_or_404(db: Session, service_id: int) -> Service:
    service = db.get(Service, service_id)  # busca por clave primaria
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service


@router.get("")
def list_services(db: DbSession) -> list[ServiceRead]:
    return db.scalars(select(Service).order_by(Service.id)).all()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_service(payload: ServiceCreate, db: DbSession) -> ServiceRead:
    service = Service(**payload.model_dump(mode="json"))  # schema → modelo
    db.add(service)  # "apúntalo para guardar"
    db.commit()  # guárdalo de verdad en Postgres
    db.refresh(service)  # relee la fila para obtener id y created_at
    return service


@router.get("/{service_id}")
def get_service(service_id: int, db: DbSession) -> ServiceRead:
    return get_service_or_404(db, service_id)


@router.patch("/{service_id}")
def update_service(service_id: int, payload: ServiceUpdate, db: DbSession) -> ServiceRead:
    service = get_service_or_404(db, service_id)
    changes = payload.model_dump(mode="json", exclude_unset=True)  # solo lo que se ha enviado
    for field, value in changes.items():
        setattr(service, field, value)
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(service_id: int, db: DbSession) -> None:
    service = get_service_or_404(db, service_id)
    db.delete(service)
    db.commit()

@router.post("/{service_id}/check", status_code=status.HTTP_201_CREATED)
def check_service_now(service_id: int, db: DbSession) -> CheckRead:
    """Lanza una comprobación inmediata de un servicio."""
    service = get_service_or_404(db, service_id)
    return run_check(db, service)


@router.get("/{service_id}/checks")
def list_checks(
    service_id: int,
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
) -> list[CheckRead]:
    """Historial de comprobaciones, de la más reciente a la más antigua."""
    get_service_or_404(db, service_id)
    stmt = (
        select(Check)
        .where(Check.service_id == service_id)
        .order_by(Check.checked_at.desc())
        .limit(limit)
    )
    return db.scalars(stmt).all()
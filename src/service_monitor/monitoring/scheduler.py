import logging
from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import func, select

from service_monitor.core.db import SessionLocal
from service_monitor.models import Check, Service
from service_monitor.monitoring.checker import run_check

logger = logging.getLogger(__name__)

TICK_SECONDS = 60
MARGIN = timedelta(seconds=10)  # tolerancia para no saltarse un tic por segundos


def check_due_services() -> None:
    """Comprueba los servicios activos que llevan más de su intervalo sin comprobarse."""
    now = datetime.now(UTC)
    with SessionLocal() as db:  # aquí no hay petición HTTP, así que abrimos la sesión a mano
        services = db.scalars(select(Service).where(Service.is_active)).all()
        for service in services:
            last_check = db.scalar(
                select(func.max(Check.checked_at)).where(Check.service_id == service.id)
            )
            interval = timedelta(minutes=service.interval_minutes)
            if last_check is None or now - last_check >= interval - MARGIN:
                check = run_check(db, service)
                logger.info("%s: %s", service.name, "UP" if check.is_up else "DOWN")


scheduler = BackgroundScheduler(timezone="UTC")
scheduler.add_job(
    check_due_services,
    "interval",
    seconds=TICK_SECONDS,
    next_run_time=datetime.now(UTC),  # primer tic al arrancar, sin esperar un minuto
    misfire_grace_time=30,  # tolera hasta 30 s de retraso en lugar de saltarse el tic
    max_instances=1,  # si un tic tarda, no se solapa con el siguiente
    coalesce=True,  # si se acumulan tics atrasados, ejecuta solo uno
)
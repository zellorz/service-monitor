import time

import httpx
from sqlalchemy.orm import Session

from service_monitor.models import Check, Service

TIMEOUT_SECONDS = 10


def run_check(db: Session, service: Service) -> Check:
    """Visita la URL del servicio y guarda el resultado como un Check."""
    start = time.perf_counter()
    try:
        response = httpx.get(service.url, timeout=TIMEOUT_SECONDS, follow_redirects=True)
        check = Check(
            service_id=service.id,
            is_up=response.is_success,  # True si el código es 2xx
            status_code=response.status_code,
            response_time_ms=int((time.perf_counter() - start) * 1000),
        )
    except httpx.HTTPError as exc:  # no respondió: DNS, timeout, conexión rechazada...
        check = Check(
            service_id=service.id,
            is_up=False,
            error=f"{type(exc).__name__}: {exc}"[:500],
        )

    db.add(check)
    db.commit()
    db.refresh(check)
    return check
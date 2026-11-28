import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from service_monitor.api.routes import health, services
from service_monitor.core.config import settings
from service_monitor.monitoring.scheduler import scheduler

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(name)s - %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if settings.scheduler_enabled:
        scheduler.start()  # al arrancar la API
    yield  # aquí la API atiende peticiones
    if scheduler.running:
        scheduler.shutdown()  # al apagarla


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.include_router(health.router)
app.include_router(services.router)
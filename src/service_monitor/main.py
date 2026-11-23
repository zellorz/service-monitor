from fastapi import FastAPI

from service_monitor.api.routes import health
from service_monitor.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(health.router)

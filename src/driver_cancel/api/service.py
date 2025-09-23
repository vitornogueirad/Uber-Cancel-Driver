from fastapi import FastAPI
from .routes import router
from ..core.config import settings
from ..core.logging import setup_logging

app = FastAPI(title="Uber Cancel Risk API", version="1.0.0")
app.include_router(router)

setup_logging(settings.log_level)

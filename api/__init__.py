from fastapi import FastAPI
from api.config import settings
from api.db import create_db
from api.route import router as route_router


def create_app():
    """
    API app loader
    """
    app = FastAPI(title=settings.app_name)
    app.include_router(route_router)
    create_db()
    return app


app = create_app()

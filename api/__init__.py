import logging

from fastapi import FastAPI

from api.auth import router as auth_router
from api.route import router as route_router
from api.config import settings
from api.db import create_db

tags_metadata = [
    {
        "name": "User",
        "description": "Operations with users. Modifying operations require authentication as an admin user",
    },
    {"name": "Token", "description": "OAuth token handling"},
]


def create_app():
    """
    API app loader
    """
    app = FastAPI(title=settings.app_name, openapi_tags=tags_metadata)
    app.include_router(route_router)
    app.include_router(auth_router)
    create_db()
    return app


app = create_app()


# start the logging (ref: https://github.com/tiangolo/fastapi/issues/1508)
@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.FileHandler("logfile.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

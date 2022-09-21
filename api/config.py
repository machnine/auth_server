from os import getenv

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Auth Server"
    admin_email: str | None
    access_token_secret: str | None
    database: str


settings = Settings(
    admin_email=getenv("ADMIN_EMAIL"),
    access_token_secret=getenv("ACCESS_TOKEN_SECRET"),
    database=getenv("DATABASE"),
)

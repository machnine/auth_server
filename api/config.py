from os import getenv

from passlib.context import CryptContext
from pydantic import BaseSettings


class Settings(BaseSettings):

    app_name: str = "Auth Server"
    admin_email: str | None = None
    access_token_secret: str | None = None    
    access_token_expiry: int = 15    # 15mins
    refresh_token_secret: str | None = None
    refresh_token_expiry: int = 1440  # 24hrs
    pwd_context: CryptContext | None = None
    database: str


settings = Settings(
    admin_email=getenv("ADMIN_EMAIL"),
    access_token_secret=getenv("ACCESS_TOKEN_SECRET"),
    refresh_token_secret=getenv("REFRESH_TOKEN_SECRET"),
    database=getenv("DATABASE"),
    pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto"),
)

from os import getenv
from typing import Optional

from passlib.context import CryptContext
from pydantic import BaseSettings


class Settings(BaseSettings):

    app_name: str = "Auth Server"
    access_token_secret: Optional[str]
    access_token_expiry: Optional[int]
    refresh_token_secret: Optional[str]
    refresh_token_expiry: Optional[int]
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
    database: str = "user.db"


settings = Settings(
    access_token_secret=getenv("ACCESS_TOKEN_SECRET"),
    refresh_token_secret=getenv("REFRESH_TOKEN_SECRET"),
    access_token_expiry=getenv("ACCESS_TOKEN_EXPIRY", 15),
    refresh_token_expiry=getenv("REFRESH_TOKEN_EXPIRY", 180),
)

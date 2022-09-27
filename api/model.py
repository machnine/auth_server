from typing import Optional

from pydantic import BaseModel, EmailStr
from sqlmodel import Column, Field, SQLModel, String


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(sa_column=Column("email", String, unique=True))
    hashed_password: str
    refresh_token: str | None = Field(default=None)
    is_admin: bool = False


class UserCreate(SQLModel):
    email: EmailStr
    password: str


class UserIn(SQLModel):
    email: EmailStr
    password: str


class UserShow(SQLModel):
    id: int
    email: EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str


class TokenRefresh(BaseModel):
    refresh_token: str

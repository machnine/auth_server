from typing import Optional
from sqlmodel import SQLModel, Field, Column, String
from pydantic import EmailStr, BaseModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(sa_column=Column("email", String, unique=True))
    hashed_password: str
    refresh_token: str | None = Field(default=None)


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
    token_type: str


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    email: EmailStr | None = None

from typing import Optional
from sqlmodel import SQLModel, Field, Column, String
from pydantic import EmailStr


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(sa_column=Column("email", String, unique=True))
    hashed_password: str


class UserCreate(SQLModel):
    email: EmailStr
    password: str


class UserShow(SQLModel):
    id: int
    email: EmailStr

from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from pydantic import EmailStr

from api.crud import create_user, delete_user, get_all_users, get_user, update_user
from api.db import Session, get_session
from api.model import UserCreate, UserShow

router = APIRouter(tags=["User"])


# User CRUD enpoints
# Create
@router.post("/user/", response_model=UserShow, status_code=status.HTTP_201_CREATED)
async def user_create(user: UserCreate, session: Session = Depends(get_session)):
    if new_user := get_user(email=user.email, session=session):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User <{new_user.email}> already exists!",
        )

    return create_user(user=user, session=session)


# Retrieve
@router.get("/users/", response_model=List[UserShow])
async def user_get_all(session: Session = Depends(get_session)):
    users = get_all_users(session=session)
    show_users = [UserShow.from_orm(user) for user in users]
    return show_users


@router.get("/user/", response_model=UserShow)
async def user_get(email: EmailStr, session: Session = Depends(get_session)):
    if user := get_user(email=email, session=session):
        return UserShow.from_orm(user)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


# Update
@router.put("/user/", response_model=UserShow)
async def user_update(
    email: EmailStr,
    password: str | None = None,
    new_email: EmailStr | None = None,
    session: Session = Depends(get_session),
):
    if get_user(email=email, session=session):
        return update_user(
            email=email, password=password, new_email=new_email, session=session
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


# Delete
@router.delete("/user/", status_code=status.HTTP_204_NO_CONTENT)
async def user_delete(email: EmailStr, session: Session = Depends(get_session)):
    if get_user(email=email, session=session):
        delete_user(email=email, session=session)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

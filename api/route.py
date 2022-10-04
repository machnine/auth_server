from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError

from api import crud
from api.auth import oauth_scheme
from api.db import Session, get_session
from api.model import UserCreate, UserShow

router = APIRouter(tags=["User"])


# User CRUD enpoints
# Create
@router.post(
    "/user/",
    response_model=UserShow,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def user_create(
    user: UserCreate,
    session: Session = Depends(get_session),
    _=Depends(oauth_scheme),
):
    if the_user := crud.get_user(email=user.email, session=session):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User <{the_user.email}> already exists!",
        )

    new_user = crud.create_user(user=user, session=session)
    return new_user


# Retrieve
@router.get(
    "/users/",
    response_model=List[UserShow],
    summary="Retrieve all users",
)
async def user_get_all(
    session: Session = Depends(get_session),
):
    users = crud.get_all_users(session=session)
    show_users = [UserShow.from_orm(user) for user in users]
    return show_users


@router.get(
    "/user/",
    response_model=UserShow,
    summary="Retrieve a user using email",
)
async def user_get(
    email: EmailStr,
    session: Session = Depends(get_session),
):
    if user := crud.get_user(email=email, session=session):
        return UserShow.from_orm(user)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


# Update
@router.put(
    "/user/",
    response_model=UserShow,
    summary="Update user attributes",
)
async def user_update(
    email: EmailStr,
    password: str | None = None,
    new_email: EmailStr | None = None,
    session: Session = Depends(get_session),
    _=Depends(oauth_scheme),
):
    if crud.get_user(email=email, session=session):
        try:
            return crud.update_user(
                email=email,
                password=password,
                new_email=new_email,
                session=session,
            )
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"<{new_email}> already exists",
            )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


# Delete
@router.delete(
    "/user/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
)
async def user_delete(
    email: EmailStr,
    session: Session = Depends(get_session),
    _=Depends(oauth_scheme),
):
    if crud.get_user(email=email, session=session):
        crud.delete_user(email=email, session=session)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

from typing import List

from sqlmodel import Session, select

from api.config import settings
from api.model import User, UserCreate, UserShow


# Create
def create_user(user: UserCreate, session: Session) -> UserShow:
    hashed_password = settings.pwd_context.hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    with session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    return UserShow.from_orm(new_user)


# Retrieve
def get_user(email: str, session: Session) -> User:
    statement = select(User).filter(User.email == email)
    with session:
        this_user = session.exec(statement).first()
    return this_user


def get_all_users(session: Session) -> List[User]:
    statement = select(User)
    with session:
        users = session.exec(statement).all()
    return users


# Update
def update_user(email: str, session: Session, **kwargs) -> User:
    this_user = get_user(email=email, session=session)
    if this_user:
        with session:
            # update password
            if password := kwargs.get("password"):
                this_user.hashed_password = settings.pwd_context.hash(password)
            # update email
            if new_email := kwargs.get("new_email"):
                this_user.email = new_email
            # update any other possible atrributes
            excluded_attrs = {"id", "email", "hashed_password"}
            for key, value in kwargs.items():
                if key in this_user.dict(exclude=excluded_attrs):
                    setattr(this_user, key, value)

            session.add(this_user)
            session.commit()
            session.refresh(this_user)
        return this_user


# Delete
def delete_user(email: str, session: Session):
    this_user = get_user(email=email, session=session)
    if this_user:
        with session:
            session.delete(this_user)
            session.commit()

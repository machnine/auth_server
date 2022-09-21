from sqlmodel import Session, select
from api.model import User, UserCreate, UserShow
from passlib.context import CryptContext


# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Create
def create_user(user: UserCreate, session: Session) -> UserShow:
    hashed_password = hash_password(user.password)
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


# Update
def update_user(email: str, session: Session, **kwargs) -> User:
    this_user = get_user(email=email, session=session)
    if this_user:
        with session:
            # update password
            if password := kwargs.get("password"):
                this_user.hashed_password = hash_password(password)
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

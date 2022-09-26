from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from api.config import settings
from api.crud import get_user, update_user
from api.db import Session, get_session
from api.model import Token, TokenRefresh, User, UserIn, UserShow

oauth_scheme = OAuth2PasswordBearer(tokenUrl="admin_token")

router = APIRouter(tags=["Token"])


def authenticate_user(user: UserIn, session: Session) -> User:
    this_user = get_user(email=user.email, session=session)

    if not this_user:
        return False

    if not settings.pwd_context.verify(user.password, this_user.hashed_password):
        return False

    return this_user


# custom exception
credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)


# JWT token
def create_jwt_token(email: str, secret: str, expires_minutes: int | None = None):
    payload = {"sub": email}
    if expires_minutes:
        expires = datetime.utcnow() + timedelta(minutes=expires_minutes)
    else:
        expires = datetime.utcnow() + timedelta(minutes=15)

    payload.update({"exp": expires})
    encoded_jwt = jwt.encode(payload, secret, algorithm="HS256")
    return encoded_jwt


def create_access_token(email: str):
    return create_jwt_token(
        email, settings.access_token_secret, settings.access_token_expiry
    )


def create_refresh_token(email: str):
    return create_jwt_token(
        email, settings.refresh_token_secret, settings.refresh_token_expiry
    )


def get_user_from_refresh_token(token: str, session: Session) -> UserShow:
    try:
        payload = jwt.decode(token, settings.refresh_token_secret, algorithms=["HS256"])
        email = payload.get("sub")
        # if user email not encoded in jwt
        if email is None:
            raise credential_exception

        # if user does not exists
        user = get_user(email=email, session=session)
        if not user:
            raise credential_exception

        # if refresh tokens do not match
        if user.refresh_token != token:
            raise credential_exception

    except JWTError:
        raise credential_exception

    return email


@router.post(
    "/admin_token/",
    response_model=Token,
    summary="Allow admin to login via webform and obtain an access token for this server",
)
async def admin_token(
    form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)
):
    user_in = UserIn(email=form.username, password=form.password)
    user = authenticate_user(user_in, session=session)
    if not user:
        raise credential_exception

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin user"
        )

    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/token/",
    response_model=Token,
    summary="Generate access_token and refresh_token for user",
)
async def access_token(user: UserIn, session: Session = Depends(get_session)):
    """
    Accept user email and password (UserIn) and generate an access token
    """
    the_user = authenticate_user(user=user, session=session)
    if not the_user:
        raise credential_exception
    access_token = create_access_token(the_user.email)  # access token expires in 15mins
    refresh_token = create_refresh_token(
        the_user.email
    )  # refresh token expires in 24hrs

    # save refresh token to db
    update_user(email=the_user.email, session=session, refresh_token=refresh_token)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/refresh/",
    response_model=Token,
    summary="Renew access_token using a valid refresh_token",
)
async def renew_access_token(
    token: TokenRefresh, session: Session = Depends(get_session)
):
    """
    Accept a refresh token and generate an access token
    """
    user = get_user_from_refresh_token(token.refresh_token, session=session)
    access_token = create_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}

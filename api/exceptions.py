from fastapi import status
from fastapi.exceptions import HTTPException


class InvalidCredentialException(HTTPException):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

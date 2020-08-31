import base64
import binascii
import os
from secrets import compare_digest
from typing import Tuple, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
)
from starlette.requests import HTTPConnection


class BasicAuth(AuthenticationBackend):
    async def authenticate(
        self, request: HTTPConnection
    ) -> Union[Tuple[AuthCredentials, SimpleUser], None]:
        if "Authorization" not in request.headers:
            return None

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            decoded = base64.b64decode(credentials).decode("ascii")
            username, _, password = decoded.partition(":")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError("Unable to parse basic auth credentials")
        correct_username = compare_digest(
            username, str(os.getenv("BASIC_AUTH_USERNAME", "test_username"))
        )
        correct_password = compare_digest(
            password,
            str(os.getenv("BASIC_AUTH_PASSWORD", "plunge-germane-tribal-pillar")),
        )
        if not (correct_username and correct_password):
            raise AuthenticationError("Invalid basic auth credentials")
        return AuthCredentials(["authenticated"]), SimpleUser(username)


def basic_auth(credentials: HTTPBasicCredentials = Depends(HTTPBasic())) -> str:
    correct_username = compare_digest(
        credentials.username, str(os.getenv("BASIC_AUTH_USERNAME", "test_username"))
    )
    correct_password = compare_digest(
        credentials.password,
        str(os.getenv("BASIC_AUTH_PASSWORD", "plunge-germane-tribal-pillar")),
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
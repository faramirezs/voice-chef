from typing import Annotated
from uuid import UUID
import jwt
import os

from fastapi import Depends, HTTPException, Request
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordBearer

from .database import get_session
from app.models import Users

# This file's responsibility is to define dependencies that can be reused
# in different parts of the application.

# -----------------------------------------------------------------------------
# Constants and Global Instances
# -----------------------------------------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_for_testing")
ALGORITHM = "HS256"
DEFAULT_TENANT_ID = UUID(os.getenv("DEFAULT_TENANT_ID", "0b796544-6414-4d62-8f1f-cd2f9f0ac0a0"))

# Security scheme for OpenAPI / Swagger UI.  auto_error=False so that cookie-based
# auth still works at runtime, but the "Authorize" button is still rendered.
_oauth2_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "")

# -----------------------------------------------------------------------------
# Internal request detection (agent secret bypass)
# -----------------------------------------------------------------------------

def _is_internal_request(request: Request) -> bool:
    """Return True if the request carries the shared internal secret header.

    Used as a temporary bypass so the agent service can call backend
    endpoints without forwarding auth headers. Only the agent container
    knows this secret. Browser-proxied requests through nginx never
    carry this header, so normal cookie/auth flow still applies.
    TODO: remove once proper auth forwarding is wired end-to-end.
    """
    if not INTERNAL_SECRET:
        return False
    return request.headers.get("X-Internal-Secret") == INTERNAL_SECRET


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------


def get_current_user(
    request: Request,
    _token: Annotated[str | None, Depends(_oauth2_optional)],
    session: Session = Depends(get_session),
) -> Users:
    """Decode the JWT from cookie or Authorization header and return the user."""

    # Quick-fix bypass for internal Docker network calls (agent -> backend).
    # TODO: remove once agent auth forwarding is properly wired.
    if _is_internal_request(request):
        return Users(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            email="internal@system.local",
            password_hash="",
            tenant_id=DEFAULT_TENANT_ID,
            role="admin",
            is_active=True,
        )

    access_token = request.cookies.get("access_token")
    if not access_token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            access_token = auth_header[7:]

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(Users).where(Users.email == email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

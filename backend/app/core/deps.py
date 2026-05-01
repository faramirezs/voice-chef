from typing import Annotated
from fastapi import Depends, HTTPException, Request
from sqlmodel import Session, select
import jwt
import os

from .database import get_session
from app.models import Users

# This file's responsibility is to define dependencies that can be reused 
# in different parts of the application.


# -----------------------------------------------------------------------------
# Constants and Global Instances
# -----------------------------------------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_for_testing")
ALGORITHM = "HS256"

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> Users:
    """Decode the JWT from cookie or Authorization header and return the user."""
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

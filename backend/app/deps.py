from typing import Annotated
from fastapi import Depends, HTTPException
from sqlmodel import Session, select
import jwt
import os

from app.database import get_session
from app.auth_utils import oauth2_scheme
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


# NOTE: mpeshko. Learning notes.
# Step 1. The oauth2_scheme object was created with 
# OAuth2PasswordBearer(tokenUrl="/auth/login"). This special object tells 
# FastAPI: "Look for an Authorization header in the request, make sure it 
# starts with `Bearer``, and extract the token string that comes after it." 
# If the header is missing or malformed, it immediately stops and returns 
# a 401 Unauthorized error.
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], # <--- Step 1
    session: Session = Depends(get_session),
) -> Users:
    """Decode the JWT and return the full User from the database."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(Users).where(Users.email == email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

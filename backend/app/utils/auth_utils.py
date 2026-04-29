import os
from sqlmodel import Session, select
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
import argon2
from password_validator import PasswordValidator
import jwt
from uuid import UUID

from app.models.users import Users

# -----------------------------------------------------------------------------
# Constants and Global Instances
# -----------------------------------------------------------------------------

# JWT signing key, algorithm, and token lifetime (for access tokens).
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_for_testing")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

ph = PasswordHasher() 

# OAuth2 scheme dependency. 
# It tells FastAPI which URL to use to get the token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# PasswordValidator schema
schema = PasswordValidator()
# Add properties to it
schema\
.min(8)\
.max(22)\
.has().uppercase()\
.has().lowercase()\
.has().digits()\
.has().symbols()\
.has().no().spaces()\

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------


def get_password_hash(password: str) -> str:
    """Hashes a password for secure database storage."""
    return ph.hash(password)


def validate_password(password: str) -> bool:
    if not schema.validate(password):
        return False
    else:
        return True


def verify_password(inserted_password: str, hashed_password: str) -> bool:
    """Checks if a provided password matches the hashed database passoword"""
    try:
        ph.verify(hashed_password, inserted_password)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False
    except argon2.exceptions.InvalidHashError:
        return False


def create_access_token(data: dict) -> str:
    """Generates a JSON Web Token for user sessions."""
    to_encode = data.copy()
   
    # Set expiration time using timezone-aware UTC
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
   
    # Encode into a jwt string
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

# NOTE: mpeshko - the exclude_id parameter is needed to reuse the helper 
# when updating a record
def ensure_unique_user_email(
        session: Session, 
        email: str,
        exclude_id: UUID | None = None
) -> None:

    query = select(Users).where((Users.email == email))
    if exclude_id:
        query = query.where(Users.id != exclude_id)
     # sends query to database and deblocks
    result = session.exec(query)
    existing_user = result.first()

    if existing_user:
        if existing_user.email == email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-Mail already registered."
            )

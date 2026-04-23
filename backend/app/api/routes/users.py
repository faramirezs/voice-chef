from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import jwt
import os
from typing import Annotated

from app.utils.auth_utils import oauth2_scheme
from app.core.database import get_session
from app.models.users import Users, Tenants
from app.schemas.users import UserSignupResponse, UserLoginResponse, TenantsResponse
from app.core.deps import get_current_user


# -----------------------------------------------------------------------------
# Constants and Global Instances
# -----------------------------------------------------------------------------

router = APIRouter(prefix="/user", tags=["Users"])

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


# ─── Routes ──────────────────────────────────────────────────────────────────

@router.get("/list_all/", response_model=list[UserSignupResponse])
async def read_users(session: Session = Depends(get_session)) -> list[UserSignupResponse]:
    """
    Retrieves a list of all users from the database.
    Returns an empty list if no users are found.
    """
    users = session.exec(select(Users)).all()
    return users

@router.get("/list_all_tenents/", response_model=list[TenantsResponse])
async def read_users(session: Session = Depends(get_session)) -> list[TenantsResponse]:
    """
    Retrieves a list of all tenants from the database.
    Returns an empty list if no tenants are found.
    """
    users = session.exec(select(Tenants)).all()
    return users


# NOTE: Mpeshko. Endpoint to test and learn how JWT token works.
@router.get("/decode-token")
async def decode_token_for_testing(token: str):
    """
    Decodes a JWT provided as a query parameter to inspect its payload.

    This is a utility endpoint for learning and testing.
    In a real application, you should use the /me endpoint with an Authorization header.
    """
    try: # Here you use your PyJWT for validation
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"decoded_payload": payload}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")


@router.get("/me", response_model=UserLoginResponse)
async def read_users_me(
    current_user: Annotated[Users, Depends(get_current_user)]
) -> UserLoginResponse:
    """
    Retrieves the profile for the currently authenticated user.
    The user is identified by the JWT token in the Authorization header.
    """
    # The get_current_user() dependency has already validated the token
    # and fetched the user object from the database.
    # We can just return it.
    return current_user

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
import os

# import files
from app.core.database import get_session
from app.models.users import Users, Tenants
from app.schemas.users import (
    UserSignupLogin, UserSignupResponse, UserLoginResponse, AuthTokenResponse
)
from app.utils.auth_utils import (
    get_password_hash, validate_password, verify_password, create_access_token,
    ensure_unique_user_email, ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.api.openapi_responses import signup_responses, login_responses


# -----------------------------------------------------------------------------
# Constants and Global Instances
# -----------------------------------------------------------------------------

router = APIRouter(prefix="/auth", tags=["Authentication"])

DEFAULT_TENANT_ID = UUID(os.getenv("DEFAULT_TENANT_ID", "0b796544-6414-4d62-8f1f-cd2f9f0ac0a0"))

# ─── Routes ──────────────────────────────────────────────────────────────────

# ─── SIGNUP ──────────────────────────────────────────────────────────────────

# mpreshko "tenant_id": "0b796544-6414-4d62-8f1f-cd2f9f0ac0a0" is hard-coded
@router.post("/signup", 
    status_code=status.HTTP_201_CREATED,
    response_model=UserSignupResponse,
    responses=signup_responses
    )
def signup(user_data: UserSignupLogin, session: Session = Depends(get_session)):
    """Handles new user registration."""
    
    # 1. Validate password strength FIRST
    if not validate_password(user_data.password):
        # The password is weak. Raise a 400 error.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is too weak. It must have a minimum of 8 characters, and include uppercase, lowercase, digits, and symbols."
        )

    # # 2. Check for unique email
    ensure_unique_user_email(session, user_data.email)

    # 3. Create a new User instance. DEFAULT_TENANT_ID is hardcoded for MVP
    try:
        target_id = DEFAULT_TENANT_ID
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format for tenant_id")
    new_user = Users(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        tenant_id=DEFAULT_TENANT_ID
    )
    
    # 4. Check if this tenant actually exists in your DB
    tenant_exists = session.get(Tenants, new_user.tenant_id)
    if not tenant_exists:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Default tenant not configured in the database.")

    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating user"
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    
    return new_user


# ─── LOGIN ──────────────────────────────────────────────────────────────────


@router.post("/login",
    status_code=status.HTTP_200_OK,
    response_model=AuthTokenResponse,
    responses=login_responses,
    )
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
) -> AuthTokenResponse:
    """Handles user login and issues a JWT"""

    # 1. Fetch user from DB. form_data has 'username' (email in our case) and 'password' fields
    query = select(Users).where(Users.email == form_data.username)
    user = session.exec(query).first()
    
    # 2. Check credentials
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 3. Check if account is disabled
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disabled. Please contact your administrator."
        )
    
    # 4. Success: Create token
    access_token = create_access_token(
        data={"sub": user.email, "id": str(user.id)})
     
    # 5. Create the user object for the response
    user_response = UserLoginResponse.model_validate(user)

    # 6. Return the full token response object
    return AuthTokenResponse(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )

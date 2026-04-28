from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from uuid import UUID
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
import os

# import our files
from app.core.database import get_session
from app.models.users import Users, Tenants
from app.schemas.users import (
    UserSignupLogin, UserSignupResponse, UserLoginResponse, AuthTokenResponse
)
from app.utils.auth_utils import (
    get_password_hash, validate_password, verify_password, create_access_token
)


# -----------------------------------------------------------------------------
# Constants and Global Instances
# -----------------------------------------------------------------------------

router = APIRouter(prefix="/auth", tags=["Authentication"])

DEFAULT_TENANT_ID = UUID(os.getenv("DEFAULT_TENANT_ID", "0b796544-6414-4d62-8f1f-cd2f9f0ac0a0"))

# ─── Routes ──────────────────────────────────────────────────────────────────

# ─── SIGNUP ──────────────────────────────────────────────────────────────────

# signup_responses are just documentation/override metadata for OpenAPI, 
# not the actual runtime response shape.
signup_responses = {
    status.HTTP_201_CREATED: {
        "description": "User created successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": "c0a8012e-0000-0000-0000-000000000001",
                    "email": "user@example.com",
                }
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict: Email or Nickname already exists",
        "content": {
            "application/json": {
                "examples": {
                    "email_exists": {
                        "summary": "Email already registered",
                        "value": {"detail": "E-Mail already registered."},
                    },
                }
            }
        },
    },
    status.HTTP_400_BAD_REQUEST: {
        "description": "Bad Request: Invalid input data",
        "content": {
            "application/json": {
                "examples": {
                    "weak_password": {
                        "summary": "Password is too weak",
                        "value": {
                            "detail": "Password is too weak. It must have a minimum of 8 characters, and include uppercase, lowercase, digits, and symbols."
                        },
                    },
                    "invalid_uuid": {
                        "summary": "Invalid UUID format",
                        "value": {"detail": "Invalid UUID format for tenant_id"},
                    },
                    "database_error": {
                        "summary": "A database error occurred",
                        "value": {"detail": "Database error: <specific_error_message>"},
                    },
                }
            }
        },
    },
    status.HTTP_503_SERVICE_UNAVAILABLE: {
        "description": "Default tenant not configured",
        "content": {
            "application/json": {
                "example": {
                    "value": "Default tenant not configured.",
                }
            }
        },
    },
}

# mpreshko "tenant_id": "0b796544-6414-4d62-8f1f-cd2f9f0ac0a0" is hard-coded
@router.post("/signup", 
    status_code=status.HTTP_201_CREATED,
    response_model=UserSignupResponse,
    responses=signup_responses
    )
async def signup(
    user_data: UserSignupLogin,
    session: Session = Depends(get_session)
):
    """Handles new user registration."""
    
    # 1. Validate password strength FIRST
    if not validate_password(user_data.password):
        # The password is weak. Raise a 400 error.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is too weak. It must have a minimum of 8 characters, and include uppercase, lowercase, digits, and symbols."
        )
    
    # 2. Check for unique email
    query = select(Users).where(Users.email == user_data.email)
    existing_user = session.exec(query).first()

    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-Mail already registered."
            )
    # 3. Create a new User instance
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

login_responses = {
    status.HTTP_200_OK: {
        "description": "User logged in successfully",
        "content": {
            "application/json": {
                "example": {
                    "access_token": "<jwt>",
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "user": {
                        "id": "b4cce9a0-7a56-4687-9aab-16cdf55f6961",
                        "tenant_id": "98aa2780-6ad4-4de0-8908-3fa799eb67db",
                        "email": "chef-admin@kitchen.local",
                        "role": "editor",
                        "is_active": "true"
                        }
                    }
                }
            },
        },
    status.HTTP_401_UNAUTHORIZED: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Invalid email or password"
                }
            }
        }
    },
    status.HTTP_403_FORBIDDEN: {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Account disabled. Please contact your administrator"
                }
            }
        }
    }
}

@router.post("/login",
    status_code=status.HTTP_200_OK,
    response_model=AuthTokenResponse,
    responses=login_responses,
    )
async def login(
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
        expires_in=3600,
        user=user_response
    )

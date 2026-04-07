from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from uuid import UUID
from fastapi.security import OAuth2PasswordRequestForm # to make the "Authorize" button work in OpenAPI
from typing import Annotated

# import our files
from app.database import get_session
from app.models.users import Users, UserSignupLogin, UserSignupResponse, Tenants, UserLoginResponse, AuthTokenResponse
from app.auth_utils import get_password_hash, validate_password, verify_password, create_access_token


# -----------------------------------------------------------------------------
# Constants and Global Instances
# -----------------------------------------------------------------------------

router = APIRouter(prefix="/auth", tags=["Authentication"])


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
        "description": "Password is too weak",
        "content": {
            "application/json": {
                "example": {
                    "value": "Password is too weak. It must have a minimum of 8 characters, and include uppercase, lowercase, digits, and symbols.",
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

# TO DO: mpreshko "tenant_id": "0b796544-6414-4d62-8f1f-cd2f9f0ac0a0" is hard-coded
@router.post(
    "/signup", 
    status_code=status.HTTP_201_CREATED,
    response_model=UserSignupResponse,
    responses=signup_responses
)
async def signup(user_data: UserSignupLogin, session: Session = Depends(get_session)
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
    query = select(Users).where(
        (Users.email == user_data.email)
    )
     # sends query to database and deblocks
    result = session.exec(query)
    existing_user = result.first()

    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-Mail already registered."
            )
    # 3. Create a new User instance. tenant_id 'f5504206-d0a6-48c0-8aa5-2ae8791be730' is hardcoded for MVP
    try:
        target_id = UUID("f5504206-d0a6-48c0-8aa5-2ae8791be730")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format for tenant_id")
    new_user = Users(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        tenant_id=target_id
    )

    # 4. Check if this tenant actually exists in your DB
    tenant_exists = session.get(Tenants, new_user.tenant_id)
    if not tenant_exists:
        raise HTTPException(
            status_code=503, 
            detail="Default tenant not configured in the database."
        )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


# ─── LOGIN ──────────────────────────────────────────────────────────────────

login_responses = {
     401: {
			"description": "Unauthorized",
			"content": {
				"application/json": {
					"example": {"detail": "Invalid email or password"}
				}
			}
	}
}

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=AuthTokenResponse,
    responses=login_responses,
    )
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
) -> AuthTokenResponse:
    """Handles user login and issues a JWT"""
    # form_data has 'username' (email in our case) and 'password' fields
    query = select(Users).where(Users.email == form_data.username)
    user = session.exec(query).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token(
        data={"sub": user.email, "id": str(user.id)})
     
    # Create the user object for the response
    user_response = UserLoginResponse.model_validate(user)

    # Return the full token response object
    return AuthTokenResponse(
        access_token=access_token,
        expires_in=3600,
        user=user_response
    )

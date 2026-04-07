from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
# from fastapi.security import OAuth2PasswordRequestForm # to make the "Authorize" button work
# from typing import Annotated

# import our files
from app.database import get_session
from app.models.users import Users, UserSignupLogin, UserSignupResponse # Token
from app.auth_utils import get_password_hash, validate_password #, verify_password, create_access_token


# -----------------------------------------------------------------------------
# Constants and Global Instances
# -----------------------------------------------------------------------------

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ─── Routes ──────────────────────────────────────────────────────────────────


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
}

# TO DO: mpreshko "tenant_id": "0b796544-6414-4d62-8f1f-cd2f9f0ac0a0" is hard-coded
@router.post(
    "/signup", 
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
    # 3. Create a new User instance
    new_user = Users(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        tenant_id="0b796544-6414-4d62-8f1f-cd2f9f0ac0a0"
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

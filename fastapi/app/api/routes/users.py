from fastapi import APIRouter, Depends #, HTTPException
from sqlmodel import Session, select
# import jwt
# import os
# from typing import Annotated
# from collections import defaultdict

# from auth_utils import oauth2_scheme
from app.database import get_session
from app.models.users import Users, UserSignupResponse, Tenants, TenantsResponse # Token 
# from dependencies import get_current_user


# -----------------------------------------------------------------------------
# Constants and Global Instances
# -----------------------------------------------------------------------------

router = APIRouter(prefix="/user", tags=["Users"])

# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = "HS256"


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

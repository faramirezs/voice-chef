from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from uuid import UUID
from typing import Annotated
from datetime import datetime

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.api_keys import APIKeys
from app.models.users import Users
from app.schemas.api_keys import (
    APIKeyCreate, APIKeyUpdate, APIKeyResponse, APIKeyCreateResponse, 
    APIKeyListResponse
)
from app.utils.api_key_utils import (
    generate_api_key, hash_api_key, get_key_preview
)


# ─── Constants and Global Instances ───────────────────────────────────────────

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


# ─── Routes ──────────────────────────────────────────────────────────────────

@router.get("", response_model=list[APIKeyListResponse])
async def list_api_keys(
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
) -> list[APIKeyListResponse]:
    """
    List all API keys for the current user's tenant.
    Requires authentication.
    """
    statement = select(APIKeys).where(APIKeys.tenant_id == current_user.tenant_id)
    api_keys = session.exec(statement).all()
    return api_keys


@router.post("", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
) -> APIKeyCreateResponse:
    """
    Create a new API key for the current user's tenant.
    The full API key is only shown once at creation time.
    Requires authentication.
    """
    # Generate a new API key
    new_key = generate_api_key()
    key_hash = hash_api_key(new_key)
    key_preview = get_key_preview(new_key)
    
    # Create the API key object
    api_key_obj = APIKeys(
        name=api_key_data.name,
        key_hash=key_hash,
        key_preview=key_preview,
        description=api_key_data.description,
        is_active=api_key_data.is_active,
        tenant_id=current_user.tenant_id,
    )
    
    try:
        session.add(api_key_obj)
        session.commit()
        session.refresh(api_key_obj)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An API key with this name already exists"
        )
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating API key"
        )
    
    return APIKeyCreateResponse(
        id=api_key_obj.id,
        name=api_key_obj.name,
        key=new_key,  # Return the full key only once
        key_preview=api_key_obj.key_preview,
        description=api_key_obj.description,
        is_active=api_key_obj.is_active,
        created_at=api_key_obj.created_at,
        tenant_id=api_key_obj.tenant_id,
    )


@router.get("/{api_key_id}", response_model=APIKeyResponse)
async def get_api_key(
    api_key_id: UUID,
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
) -> APIKeyResponse:
    """
    Retrieve a specific API key by ID.
    Requires authentication and ownership of the API key.
    """
    api_key_obj = session.get(APIKeys, api_key_id)
    
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    if api_key_obj.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this API key"
        )
    
    return api_key_obj


@router.patch("/{api_key_id}", response_model=APIKeyResponse)
async def update_api_key(
    api_key_id: UUID,
    api_key_update: APIKeyUpdate,
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
) -> APIKeyResponse:
    """
    Update an API key (name, description, or active status).
    The actual key cannot be updated; a new key must be created.
    Requires authentication and ownership of the API key.
    """
    api_key_obj = session.get(APIKeys, api_key_id)
    
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    if api_key_obj.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this API key"
        )
    
    # Update fields
    if api_key_update.name is not None:
        api_key_obj.name = api_key_update.name
    if api_key_update.description is not None:
        api_key_obj.description = api_key_update.description
    if api_key_update.is_active is not None:
        api_key_obj.is_active = api_key_update.is_active
    
    api_key_obj.updated_at = datetime.utcnow()
    
    try:
        session.add(api_key_obj)
        session.commit()
        session.refresh(api_key_obj)
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating API key"
        )
    
    return api_key_obj


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: UUID,
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user),
) -> None:
    """
    Delete an API key.
    Requires authentication and ownership of the API key.
    """
    api_key_obj = session.get(APIKeys, api_key_id)
    
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    if api_key_obj.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this API key"
        )
    
    try:
        session.delete(api_key_obj)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting API key"
        )

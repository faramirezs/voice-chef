from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import Annotated

from app.core.deps import get_current_user
from app.models.users import Users
from app.schemas.api_keys import (
    APIKeyCreate, APIKeyUpdate, APIKeyResponse, APIKeyCreateResponse, 
    APIKeyListResponse
)
from app.services.api_keys import APIKeyService


# ─── Constants and Global Instances ───────────────────────────────────────────

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


# ─── Routes ──────────────────────────────────────────────────────────────────

@router.get("", response_model=list[APIKeyListResponse])
async def list_api_keys(
    current_user: Users = Depends(get_current_user),
) -> list[APIKeyListResponse]:
    """
    List all API keys for the current user's tenant.
    Requires authentication.
    """
    return APIKeyService.list_api_keys(current_user.tenant_id)


@router.post("", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: Users = Depends(get_current_user),
) -> APIKeyCreateResponse:
    """
    Create a new API key for the current user's tenant.
    The full API key is only shown once at creation time.
    Requires authentication.
    """
    return APIKeyService.create_api_key(current_user.tenant_id, api_key_data)


@router.get("/{api_key_id}", response_model=APIKeyListResponse)
async def get_api_key(
    api_key_id: UUID,
    current_user: Users = Depends(get_current_user),
) -> APIKeyListResponse:
    """
    Retrieve a specific API key by ID.
    Requires authentication and ownership of the API key.
    """
    return APIKeyService.get_api_key(current_user.tenant_id, api_key_id)


@router.patch("/{api_key_id}", response_model=APIKeyListResponse)
async def update_api_key(
    api_key_id: UUID,
    api_key_update: APIKeyUpdate,
    current_user: Users = Depends(get_current_user),
) -> APIKeyListResponse:
    """
    Update an API key (name, description, or active status).
    The actual key cannot be updated; a new key must be created.
    Requires authentication and ownership of the API key.
    """
    return APIKeyService.update_api_key(current_user.tenant_id, api_key_id, api_key_update)


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: UUID,
    current_user: Users = Depends(get_current_user),
) -> None:
    """
    Delete an API key.
    Requires authentication and ownership of the API key.
    """
    APIKeyService.delete_api_key(current_user.tenant_id, api_key_id)

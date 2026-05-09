from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import Annotated, List
from datetime import datetime

from app.core.deps import get_current_user
from app.models.users import Users
from app.schemas.api_keys import (
    APIKeyCreate, APIKeyUpdate, APIKeyResponse, APIKeyCreateResponse, 
    APIKeyListResponse
)
from app.utils.api_key_utils import (
    generate_api_key, hash_api_key, get_key_preview,
    _load_tenant_key, _save_tenant_key
)


# ─── Constants and Global Instances ───────────────────────────────────────────

router = APIRouter(prefix="/api_keys", tags=["API Keys"])


# ─── Helper Functions ────────────────────────────────────────────────────────

def list_api_keys_for_tenant(tenant_id: UUID) -> List[APIKeyListResponse]:
    """
    Get the API key for a tenant.
    
    Args:
        tenant_id: The tenant ID
        
    Returns:
        List containing the single API key if it exists, otherwise empty
    """
    key_data = _load_tenant_key(tenant_id)
    
    if not key_data:
        return []
    
    return [APIKeyListResponse(
        id=UUID(key_data['id']),
        name=key_data['name'],
        key_preview=key_data['key_preview'],
        description=key_data.get('description'),
        is_active=key_data.get('is_active', True),
        created_at=datetime.fromisoformat(key_data['created_at']),
        updated_at=datetime.fromisoformat(key_data['updated_at']),
        last_used_at=datetime.fromisoformat(key_data['last_used_at']) if key_data.get('last_used_at') else None,
        tenant_id=tenant_id,
    )]


def get_api_key_for_tenant(tenant_id: UUID, key_id: UUID = None) -> APIKeyListResponse:
    """
    Get the API key for a tenant. The key_id parameter is ignored since there's only one key per tenant.
    
    Args:
        tenant_id: The tenant ID
        key_id: Ignored (kept for API compatibility)
        
    Returns:
        The API key response
        
    Raises:
        HTTPException: If no key exists for the tenant
    """
    key_data = _load_tenant_key(tenant_id)
    
    if not key_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return APIKeyListResponse(
        id=UUID(key_data['id']),
        name=key_data['name'],
        key_preview=key_data['key_preview'],
        description=key_data.get('description'),
        is_active=key_data.get('is_active', True),
        created_at=datetime.fromisoformat(key_data['created_at']),
        updated_at=datetime.fromisoformat(key_data['updated_at']),
        last_used_at=datetime.fromisoformat(key_data['last_used_at']) if key_data.get('last_used_at') else None,
        tenant_id=tenant_id,
    )


def create_api_key_for_tenant(tenant_id: UUID, api_key_data: APIKeyCreate) -> APIKeyCreateResponse:
    """
    Create a new API key for a tenant. If a key already exists, it will be replaced.
    
    Args:
        tenant_id: The tenant ID
        api_key_data: The API key creation data
        
    Returns:
        The created API key response (with full key)
    """
    # Generate new key
    new_key = generate_api_key()
    key_hash = hash_api_key(new_key)
    key_preview = get_key_preview(new_key)
    
    from uuid import uuid4
    key_id = str(uuid4())
    
    now = datetime.utcnow()
    
    # Create the key data
    key_data = {
        'id': key_id,
        'name': api_key_data.name,
        'key_hash': key_hash,
        'key_preview': key_preview,
        'description': api_key_data.description,
        'is_active': api_key_data.is_active if api_key_data.is_active is not None else True,
        'created_at': now.isoformat(),
        'updated_at': now.isoformat(),
        'last_used_at': None,
    }
    
    _save_tenant_key(tenant_id, key_data)
    
    return APIKeyCreateResponse(
        id=UUID(key_id),
        name=api_key_data.name,
        key=new_key,
        key_preview=key_preview,
        description=api_key_data.description,
        is_active=key_data['is_active'],
        created_at=now,
        tenant_id=tenant_id,
    )


def update_api_key_for_tenant(
    tenant_id: UUID, 
    key_id: UUID = None, 
    api_key_update: APIKeyUpdate = None
) -> APIKeyListResponse:
    """
    Update the API key for a tenant. The key_id parameter is ignored.
    
    Args:
        tenant_id: The tenant ID
        key_id: Ignored (kept for API compatibility)
        api_key_update: The update data
        
    Returns:
        The updated API key response
        
    Raises:
        HTTPException: If key not found or update fails
    """
    key_data = _load_tenant_key(tenant_id)
    
    if not key_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Update fields
    if api_key_update.name is not None:
        key_data['name'] = api_key_update.name
    
    if api_key_update.description is not None:
        key_data['description'] = api_key_update.description
    
    if api_key_update.is_active is not None:
        key_data['is_active'] = api_key_update.is_active
    
    key_data['updated_at'] = datetime.utcnow().isoformat()
    
    _save_tenant_key(tenant_id, key_data)
    
    return APIKeyListResponse(
        id=UUID(key_data['id']),
        name=key_data['name'],
        key_preview=key_data['key_preview'],
        description=key_data.get('description'),
        is_active=key_data.get('is_active', True),
        created_at=datetime.fromisoformat(key_data['created_at']),
        updated_at=datetime.fromisoformat(key_data['updated_at']),
        last_used_at=datetime.fromisoformat(key_data['last_used_at']) if key_data.get('last_used_at') else None,
        tenant_id=tenant_id,
    )


def delete_api_key_for_tenant(tenant_id: UUID, key_id: UUID = None) -> None:
    """
    Delete the API key for a tenant. The key_id parameter is ignored.
    
    Args:
        tenant_id: The tenant ID
        key_id: Ignored (kept for API compatibility)
        
    Raises:
        HTTPException: If no key exists
    """
    key_data = _load_tenant_key(tenant_id)
    
    if not key_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Delete the file to remove the key
    from app.utils.api_key_utils import _get_tenant_file
    file_path = _get_tenant_file(tenant_id)
    try:
        file_path.unlink()
    except FileNotFoundError:
        pass


def validate_api_key_for_tenant(key_hash: str, tenant_id: UUID) -> str | None:
    """
    Validate an API key hash against the stored key for a tenant.
    
    Args:
        key_hash: The hash of the API key to validate
        tenant_id: The tenant ID
        
    Returns:
        The key ID if valid and active, None otherwise
    """
    key_data = _load_tenant_key(tenant_id)
    
    if (key_data and 
        key_data['key_hash'] == key_hash and 
        key_data.get('is_active', True)):
        return key_data['id']
    
    return None


def update_last_used_for_tenant(tenant_id: UUID, key_id: str = None) -> None:
    """
    Update the last_used_at timestamp for the API key. The key_id parameter is ignored.
    
    Args:
        tenant_id: The tenant ID
        key_id: Ignored (kept for compatibility)
    """
    key_data = _load_tenant_key(tenant_id)
    
    if key_data:
        key_data['last_used_at'] = datetime.utcnow().isoformat()
        _save_tenant_key(tenant_id, key_data)


# ─── Routes ──────────────────────────────────────────────────────────────────

@router.get("", response_model=list[APIKeyListResponse])
async def list_api_keys(
    current_user: Users = Depends(get_current_user),
) -> list[APIKeyListResponse]:
    """
    List all API keys for the current user's tenant.
    Requires authentication.
    """
    return list_api_keys_for_tenant(current_user.tenant_id)


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
    return create_api_key_for_tenant(current_user.tenant_id, api_key_data)


@router.get("/{api_key_id}", response_model=APIKeyListResponse)
async def get_api_key(
    api_key_id: UUID,
    current_user: Users = Depends(get_current_user),
) -> APIKeyListResponse:
    """
    Retrieve a specific API key by ID.
    Requires authentication and ownership of the API key.
    """
    return get_api_key_for_tenant(current_user.tenant_id, api_key_id)


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
    return update_api_key_for_tenant(current_user.tenant_id, api_key_id, api_key_update)


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: UUID,
    current_user: Users = Depends(get_current_user),
) -> None:
    """
    Delete an API key.
    Requires authentication and ownership of the API key.
    """
    delete_api_key_for_tenant(current_user.tenant_id, api_key_id)

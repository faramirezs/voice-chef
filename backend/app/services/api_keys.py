import json
import os
from pathlib import Path
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from fastapi import HTTPException, status

from app.schemas.api_keys import (
    APIKeyCreate, APIKeyUpdate, APIKeyListResponse, APIKeyCreateResponse
)
from app.utils.api_key_utils import (
    generate_api_key, hash_api_key, get_key_preview
)


# ─── Constants ────────────────────────────────────────────────────────────────

API_KEYS_DIR = Path("data/api_keys")


# ─── Helper Functions ────────────────────────────────────────────────────────

def _ensure_api_keys_dir() -> None:
    """Ensure the API keys directory exists."""
    API_KEYS_DIR.mkdir(parents=True, exist_ok=True)


def _get_tenant_file(tenant_id: UUID) -> Path:
    """Get the file path for a tenant's API keys."""
    _ensure_api_keys_dir()
    return API_KEYS_DIR / f"{tenant_id}.json"


def _load_tenant_key(tenant_id: UUID) -> Optional[dict]:
    """Load the API key for a tenant from file."""
    file_path = _get_tenant_file(tenant_id)
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _save_tenant_key(tenant_id: UUID, key_data: dict) -> None:
    """Save the API key for a tenant to file."""
    file_path = _get_tenant_file(tenant_id)
    _ensure_api_keys_dir()
    
    with open(file_path, 'w') as f:
        json.dump(key_data, f, indent=2, default=str)


# ─── API Key Service ────────────────────────────────────────────────────────

class APIKeyService:
    """Service for managing API keys with file-based storage."""
    
    @staticmethod
    def list_api_keys(tenant_id: UUID) -> List[APIKeyListResponse]:
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
    
    @staticmethod
    def get_api_key(tenant_id: UUID, key_id: UUID = None) -> APIKeyListResponse:
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
    
    @staticmethod
    def create_api_key(tenant_id: UUID, api_key_data: APIKeyCreate) -> APIKeyCreateResponse:
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
    
    @staticmethod
    def update_api_key(
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
    
    @staticmethod
    def delete_api_key(tenant_id: UUID, key_id: UUID = None) -> None:
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
        file_path = _get_tenant_file(tenant_id)
        try:
            file_path.unlink()
        except FileNotFoundError:
            pass
    
    @staticmethod
    def validate_api_key(key_hash: str, tenant_id: UUID) -> Optional[str]:
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
    
    @staticmethod
    def update_last_used(tenant_id: UUID, key_id: str = None) -> None:
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

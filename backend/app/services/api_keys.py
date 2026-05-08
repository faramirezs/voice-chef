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


def _load_tenant_keys(tenant_id: UUID) -> dict:
    """Load all API keys for a tenant from file."""
    file_path = _get_tenant_file(tenant_id)
    if not file_path.exists():
        return {}
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_tenant_keys(tenant_id: UUID, keys_data: dict) -> None:
    """Save all API keys for a tenant to file."""
    file_path = _get_tenant_file(tenant_id)
    _ensure_api_keys_dir()
    
    with open(file_path, 'w') as f:
        json.dump(keys_data, f, indent=2, default=str)


# ─── API Key Service ────────────────────────────────────────────────────────

class APIKeyService:
    """Service for managing API keys with file-based storage."""
    
    @staticmethod
    def list_api_keys(tenant_id: UUID) -> List[APIKeyListResponse]:
        """
        List all API keys for a tenant.
        
        Args:
            tenant_id: The tenant ID
            
        Returns:
            List of API key responses
        """
        keys_data = _load_tenant_keys(tenant_id)
        
        api_keys = []
        for key_id, key_info in keys_data.items():
            api_keys.append(APIKeyListResponse(
                id=UUID(key_id),
                name=key_info['name'],
                key_preview=key_info['key_preview'],
                description=key_info.get('description'),
                is_active=key_info.get('is_active', True),
                created_at=datetime.fromisoformat(key_info['created_at']),
                updated_at=datetime.fromisoformat(key_info['updated_at']),
                last_used_at=datetime.fromisoformat(key_info['last_used_at']) if key_info.get('last_used_at') else None,
                tenant_id=tenant_id,
            ))
        
        return api_keys
    
    @staticmethod
    def get_api_key(tenant_id: UUID, key_id: UUID) -> APIKeyListResponse:
        """
        Get a specific API key by ID.
        
        Args:
            tenant_id: The tenant ID
            key_id: The API key ID
            
        Returns:
            The API key response
            
        Raises:
            HTTPException: If key not found or not owned by tenant
        """
        keys_data = _load_tenant_keys(tenant_id)
        key_id_str = str(key_id)
        
        if key_id_str not in keys_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        key_info = keys_data[key_id_str]
        return APIKeyListResponse(
            id=key_id,
            name=key_info['name'],
            key_preview=key_info['key_preview'],
            description=key_info.get('description'),
            is_active=key_info.get('is_active', True),
            created_at=datetime.fromisoformat(key_info['created_at']),
            updated_at=datetime.fromisoformat(key_info['updated_at']),
            last_used_at=datetime.fromisoformat(key_info['last_used_at']) if key_info.get('last_used_at') else None,
            tenant_id=tenant_id,
        )
    
    @staticmethod
    def create_api_key(tenant_id: UUID, api_key_data: APIKeyCreate) -> APIKeyCreateResponse:
        """
        Create a new API key for a tenant.
        
        Args:
            tenant_id: The tenant ID
            api_key_data: The API key creation data
            
        Returns:
            The created API key response (with full key)
        """
        keys_data = _load_tenant_keys(tenant_id)
        
        # Check if name already exists
        for key_info in keys_data.values():
            if key_info['name'] == api_key_data.name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An API key with this name already exists"
                )
        
        # Generate new key
        new_key = generate_api_key()
        key_hash = hash_api_key(new_key)
        key_preview = get_key_preview(new_key)
        key_id = UUID(int=0).hex[:8]  # Simple ID generation, can be improved
        
        # Import UUID to generate proper ID
        from uuid import uuid4
        key_id = str(uuid4())
        
        now = datetime.utcnow()
        
        # Store the key info (without the full key)
        keys_data[key_id] = {
            'id': key_id,
            'name': api_key_data.name,
            'key_hash': key_hash,
            'key_preview': key_preview,
            'description': api_key_data.description,
            'is_active': api_key_data.is_active,
            'created_at': now.isoformat(),
            'updated_at': now.isoformat(),
            'last_used_at': None,
        }
        
        _save_tenant_keys(tenant_id, keys_data)
        
        return APIKeyCreateResponse(
            id=UUID(key_id),
            name=api_key_data.name,
            key=new_key,
            key_preview=key_preview,
            description=api_key_data.description,
            is_active=api_key_data.is_active,
            created_at=now,
            tenant_id=tenant_id,
        )
    
    @staticmethod
    def update_api_key(
        tenant_id: UUID, 
        key_id: UUID, 
        api_key_update: APIKeyUpdate
    ) -> APIKeyListResponse:
        """
        Update an API key.
        
        Args:
            tenant_id: The tenant ID
            key_id: The API key ID
            api_key_update: The update data
            
        Returns:
            The updated API key response
            
        Raises:
            HTTPException: If key not found or update fails
        """
        keys_data = _load_tenant_keys(tenant_id)
        key_id_str = str(key_id)
        
        if key_id_str not in keys_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        key_info = keys_data[key_id_str]
        
        # Update fields
        if api_key_update.name is not None:
            # Check if new name already exists
            for other_id, other_info in keys_data.items():
                if other_id != key_id_str and other_info['name'] == api_key_update.name:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="An API key with this name already exists"
                    )
            key_info['name'] = api_key_update.name
        
        if api_key_update.description is not None:
            key_info['description'] = api_key_update.description
        
        if api_key_update.is_active is not None:
            key_info['is_active'] = api_key_update.is_active
        
        key_info['updated_at'] = datetime.utcnow().isoformat()
        
        _save_tenant_keys(tenant_id, keys_data)
        
        return APIKeyListResponse(
            id=key_id,
            name=key_info['name'],
            key_preview=key_info['key_preview'],
            description=key_info.get('description'),
            is_active=key_info.get('is_active', True),
            created_at=datetime.fromisoformat(key_info['created_at']),
            updated_at=datetime.fromisoformat(key_info['updated_at']),
            last_used_at=datetime.fromisoformat(key_info['last_used_at']) if key_info.get('last_used_at') else None,
            tenant_id=tenant_id,
        )
    
    @staticmethod
    def delete_api_key(tenant_id: UUID, key_id: UUID) -> None:
        """
        Delete an API key.
        
        Args:
            tenant_id: The tenant ID
            key_id: The API key ID
            
        Raises:
            HTTPException: If key not found
        """
        keys_data = _load_tenant_keys(tenant_id)
        key_id_str = str(key_id)
        
        if key_id_str not in keys_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        del keys_data[key_id_str]
        _save_tenant_keys(tenant_id, keys_data)
    
    @staticmethod
    def validate_api_key(key_hash: str, tenant_id: UUID) -> Optional[str]:
        """
        Validate an API key hash against stored keys.
        
        Args:
            key_hash: The hash of the API key to validate
            tenant_id: The tenant ID
            
        Returns:
            The key ID if valid and active, None otherwise
        """
        keys_data = _load_tenant_keys(tenant_id)
        
        for key_id, key_info in keys_data.items():
            if (key_info['key_hash'] == key_hash and 
                key_info.get('is_active', True)):
                return key_id
        
        return None
    
    @staticmethod
    def update_last_used(tenant_id: UUID, key_id: str) -> None:
        """
        Update the last_used_at timestamp for an API key.
        
        Args:
            tenant_id: The tenant ID
            key_id: The API key ID
        """
        keys_data = _load_tenant_keys(tenant_id)
        
        if key_id in keys_data:
            keys_data[key_id]['last_used_at'] = datetime.utcnow().isoformat()
            _save_tenant_keys(tenant_id, keys_data)

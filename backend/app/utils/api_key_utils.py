import hashlib
import json
import secrets
from pathlib import Path
from fastapi import Depends, HTTPException, status, Request
from typing import Optional, Tuple
from uuid import UUID
from datetime import datetime


# ─── Constants ────────────────────────────────────────────────────────────────

API_KEY_PREFIX = "vchef_"
API_KEY_LENGTH = 32  # Length of the random part
API_KEYS_DIR = Path("/code/data/api_keys")


# ─── Utility Functions ────────────────────────────────────────────────────────

def generate_api_key() -> str:
    """
    Generate a new API key with format: vchef_<random_32_chars>
    
    Returns:
        str: A newly generated API key
    """
    random_part = secrets.token_urlsafe(API_KEY_LENGTH)
    return f"{API_KEY_PREFIX}{random_part}"


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key using SHA-256.
    
    Args:
        api_key: The API key to hash
        
    Returns:
        str: SHA-256 hash of the API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def get_key_preview(api_key: str) -> str:
    """
    Generate a preview of the API key (first 4 and last 4 characters).
    
    Args:
        api_key: The API key to preview
        
    Returns:
        str: A preview string like "vche...xxxx"
    """
    if len(api_key) <= 8:
        return api_key
    return f"{api_key[:4]}...{api_key[-4:]}"


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


async def validate_api_key(
    request: Request,
) -> Optional[Tuple[UUID, str]]:
    """
    Dependency to validate API key from X-API-Key header.
    
    If an API key is provided in the header, it validates it and returns the
    corresponding (tenant_id, key_id) tuple. If no API key is provided, returns None.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Optional[Tuple[UUID, str]]: A tuple of (tenant_id, key_id) if valid, None if not provided
        
    Raises:
        HTTPException: If API key is invalid or inactive
    """
    api_key_header = request.headers.get("X-API-Key")
    
    if not api_key_header:
        # Optional - return None if no key provided
        return None
    
    # Hash the provided key
    key_hash = hash_api_key(api_key_header)
    
    # Search through all tenant files
    if API_KEYS_DIR.exists():
        for tenant_file in API_KEYS_DIR.glob("*.json"):
            try:
                with open(tenant_file, 'r') as f:
                    key_data = json.load(f)
                
                if (key_data and 
                    key_data.get('key_hash') == key_hash and 
                    key_data.get('is_active', True)):
                    # Extract tenant_id from filename
                    tenant_id_str = tenant_file.stem
                    tenant_id = UUID(tenant_id_str)
                    key_id = key_data.get('id', 'default')
                    
                    # Update last_used_at timestamp
                    key_data['last_used_at'] = datetime.utcnow().isoformat()
                    
                    try:
                        with open(tenant_file, 'w') as f:
                            json.dump(key_data, f, indent=2, default=str)
                    except Exception:
                        # Don't fail if we can't update timestamp
                        pass
                    
                    return (tenant_id, key_id)
            except (json.JSONDecodeError, IOError, ValueError):
                continue
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key"
    )

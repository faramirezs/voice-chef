import hashlib
import secrets
from fastapi import Depends, HTTPException, status, Request
from sqlmodel import Session, select
from typing import Optional, Annotated

from app.core.database import get_session
from app.models.api_keys import APIKeys


# ─── Constants ────────────────────────────────────────────────────────────────

API_KEY_PREFIX = "vchef_"
API_KEY_LENGTH = 32  # Length of the random part


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


async def validate_api_key(
    request: Request,
    session: Session = Depends(get_session)
) -> Optional[APIKeys]:
    """
    Dependency to validate API key from X-API-Key header.
    
    If an API key is provided in the header, it validates it and returns the
    corresponding APIKeys model. If no API key is provided, returns None.
    
    Args:
        request: FastAPI Request object
        session: Database session
        
    Returns:
        Optional[APIKeys]: The APIKeys object if valid, None if not provided
        
    Raises:
        HTTPException: If API key is invalid or inactive
    """
    api_key_header = request.headers.get("X-API-Key")
    
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header"
        )
    
    # Hash the provided key
    key_hash = hash_api_key(api_key_header)
    
    # Look up the key in the database
    statement = select(APIKeys).where(
        APIKeys.key_hash == key_hash,
        APIKeys.is_active == True
    )
    api_key_obj = session.exec(statement).first()
    
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Update last_used_at timestamp
    from datetime import datetime
    api_key_obj.last_used_at = datetime.utcnow()
    session.add(api_key_obj)
    try:
        session.commit()
    except Exception:
        session.rollback()
        # Don't fail the request if we can't update the timestamp
        pass
    
    return api_key_obj

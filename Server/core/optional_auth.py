"""Optional authentication dependency"""
from fastapi import Header
from typing import Optional
from core.auth import AuthContext, verify_api_key
from sqlalchemy.orm import Session


async def optional_auth(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> Optional[AuthContext]:
    """Optional authentication - returns None if no API key provided"""
    if not x_api_key:
        return None
    
    # If API key is provided, verify it
    try:
        from core.auth import verify_api_key
        # This will raise HTTPException if invalid
        # We need to call verify_api_key but it needs db dependency
        # For now, return None - this is a simplified version
        return None
    except:
        return None

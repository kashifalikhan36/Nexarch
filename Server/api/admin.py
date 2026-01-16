
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.base import get_db
from db.models import Tenant, User, APIKey as DBAPIKey
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime
import uuid
import secrets

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


class CreateTenantRequest(BaseModel):
    name: str
    admin_email: EmailStr


class TenantResponse(BaseModel):
    id: str
    name: str
    api_key: str
    admin_email: str
    created_at: datetime


@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(request: CreateTenantRequest, db: Session = Depends(get_db)):
    """Create new tenant with admin user and API key (PUBLIC - NO AUTH REQUIRED)"""
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.admin_email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create tenant
    tenant_id = str(uuid.uuid4())
    tenant = Tenant(
        id=tenant_id,
        name=request.name,
        created_at=datetime.now(),
        is_active=True
    )
    db.add(tenant)
    
    # Create admin user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=request.admin_email,
        tenant_id=tenant_id,
        created_at=datetime.now(),
        is_active=True
    )
    db.add(user)
    
    # Generate API key
    api_key = f"nex_{secrets.token_urlsafe(32)}"
    api_key_obj = DBAPIKey(
        key=api_key,
        tenant_id=tenant_id,
        user_id=user_id,
        name="Default API Key",
        is_active=True,
        created_at=datetime.now()
    )
    db.add(api_key_obj)
    
    db.commit()
    
    return TenantResponse(
        id=tenant_id,
        name=request.name,
        api_key=api_key,
        admin_email=request.admin_email,
        created_at=tenant.created_at
    )


@router.get("/tenants")
async def list_tenants(db: Session = Depends(get_db)):
    """List all tenants"""
    tenants = db.query(Tenant).all()
    return [{"id": t.id, "name": t.name, "is_active": t.is_active, "created_at": t.created_at.isoformat()} for t in tenants]


@router.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str, db: Session = Depends(get_db)):
    """Get tenant details"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Get user count
    user_count = db.query(User).filter(User.tenant_id == tenant_id).count()
    
    # Get API key count
    key_count = db.query(DBAPIKey).filter(DBAPIKey.tenant_id == tenant_id).count()
    
    return {
        "id": tenant.id,
        "name": tenant.name,
        "is_active": tenant.is_active,
        "created_at": tenant.created_at.isoformat(),
        "max_spans_per_day": tenant.max_spans_per_day,
        "user_count": user_count,
        "api_key_count": key_count
    }


@router.patch("/tenants/{tenant_id}")
async def update_tenant(
    tenant_id: str,
    is_active: bool = None,
    name: str = None,
    max_spans_per_day: int = None,
    db: Session = Depends(get_db)
):
    """Update tenant settings"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if is_active is not None:
        tenant.is_active = is_active
    if name is not None:
        tenant.name = name
    if max_spans_per_day is not None:
        tenant.max_spans_per_day = max_spans_per_day
    
    db.commit()
    
    return {
        "id": tenant.id,
        "name": tenant.name,
        "is_active": tenant.is_active,
        "max_spans_per_day": tenant.max_spans_per_day,
        "message": "Tenant updated successfully"
    }


@router.delete("/tenants/{tenant_id}")
async def delete_tenant(tenant_id: str, db: Session = Depends(get_db)):
    """
    Delete tenant and all associated data (USE WITH CAUTION).
    This is a soft delete - sets is_active to False.
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Soft delete - deactivate instead of deleting
    tenant.is_active = False
    
    # Also deactivate all API keys
    db.query(DBAPIKey).filter(DBAPIKey.tenant_id == tenant_id).update({"is_active": False})
    
    db.commit()
    
    return {
        "message": f"Tenant {tenant_id} deactivated successfully",
        "tenant_id": tenant_id
    }


@router.post("/tenants/{tenant_id}/api-keys")
async def create_api_key(
    tenant_id: str,
    name: str,
    db: Session = Depends(get_db)
):
    """Create new API key for tenant"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id, Tenant.is_active == True).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found or inactive")
    
    # Generate new API key
    api_key = f"nex_{secrets.token_urlsafe(32)}"
    api_key_obj = DBAPIKey(
        key=api_key,
        tenant_id=tenant_id,
        user_id=None,
        name=name,
        is_active=True,
        created_at=datetime.now()
    )
    db.add(api_key_obj)
    db.commit()
    
    return {
        "api_key": api_key,
        "name": name,
        "created_at": api_key_obj.created_at.isoformat()
    }


@router.get("/tenants/{tenant_id}/api-keys")
async def list_api_keys(tenant_id: str, db: Session = Depends(get_db)):
    """List API keys for tenant (masked)"""
    keys = db.query(DBAPIKey).filter(DBAPIKey.tenant_id == tenant_id).all()
    
    return [
        {
            "key": f"{k.key[:8]}...{k.key[-4:]}",
            "name": k.name,
            "is_active": k.is_active,
            "created_at": k.created_at.isoformat(),
            "last_used": k.last_used.isoformat() if k.last_used else None
        }
        for k in keys
    ]


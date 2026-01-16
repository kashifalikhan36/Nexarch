
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
    return [{"id": t.id, "name": t.name, "is_active": t.is_active} for t in tenants]

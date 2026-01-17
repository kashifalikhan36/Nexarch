"""
CRUD operations for User model
"""
from typing import Optional
from db.models import User
from db.base import get_db
from datetime import datetime
from sqlalchemy.orm import Session
import uuid


def get_user_by_id(user_id: str, db: Session = None) -> Optional[User]:
    """
    Get user by ID
    
    Args:
        user_id: User ID string
        db: Database session
        
    Returns:
        User object or None if not found
    """
    if db is None:
        db = next(get_db())
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except Exception as e:
        print(f"Error getting user by ID: {e}")
        return None


def get_user_by_email(email: str, db: Session = None) -> Optional[User]:
    """
    Get user by email
    
    Args:
        email: User email address
        db: Database session
        
    Returns:
        User object or None if not found
    """
    if db is None:
        db = next(get_db())
    
    try:
        user = db.query(User).filter(User.email == email.lower()).first()
        return user
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None


def create_google_user(
    email: str,
    google_id: str,
    full_name: Optional[str] = None,
    picture: Optional[str] = None,
    db: Session = None,
) -> User:
    """
    Create or update Google OAuth user
    
    Args:
        email: User email from Google
        google_id: Google user ID
        full_name: User's full name
        picture: Profile picture URL
        db: Database session
        
    Returns:
        User object
    """
    if db is None:
        db = next(get_db())
    
    # Check if user exists
    existing_user = get_user_by_email(email, db)
    
    if existing_user:
        # Update existing user with Google info
        existing_user.google_id = google_id
        existing_user.auth_provider = "google"
        existing_user.is_active = True
        existing_user.is_verified = True
        if full_name:
            existing_user.full_name = full_name
        if picture:
            existing_user.picture = picture
        existing_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_user)
        return existing_user
    
    # Create new user
    new_user = User(
        id=str(uuid.uuid4()),
        email=email.lower(),
        google_id=google_id,
        full_name=full_name or email.split("@")[0],
        picture=picture,
        auth_provider="google",
        is_active=True,
        is_verified=True,
        pending_signup=False,
        tenant_id=None,  # No tenant initially for OAuth users
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

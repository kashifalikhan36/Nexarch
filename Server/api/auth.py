"""
Authentication Router - Google OAuth Only
FastAPI server: https://api.modelix.world
Frontend: https://run-time.in
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from datetime import datetime
from typing import Dict, Any

from core.config import get_settings
from core.security import create_access_token
from db.models import User
from Schemas.user import (
    UserMeResponse,
    GoogleAuthRequestWithState,
)
from Schemas.token import TokenResponse, GoogleAuthUrlResponse
from dependencies.auth import get_current_user, get_current_active_user
from crud.user import (
    get_user_by_id,
    create_google_user,
)
from utils.google_oauth import get_google_oauth_client
from utils.redis_client import cache_delete

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()

# ==================== GET CURRENT USER ====================
@router.get("/me", response_model=UserMeResponse)
async def get_me(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get current authenticated user's information.
    
    **Authentication:**
    - Requires valid JWT token in Authorization header: `Bearer <token>`
    
    **Returns:**
    - User details including email, name, creation date, etc.
    """
    # Fetch full user details from database
    user = await get_user_by_id(current_user["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserMeResponse(
        id=str(user.id),
        email=user.email,
        name=user.full_name or user.email.split("@")[0],
        role="user",  # Default role
        created_at=user.created_at,
    )



# ==================== GOOGLE OAUTH ====================
@router.get("/google", response_model=GoogleAuthUrlResponse)
async def get_google_auth_url():
    """
    Get the Google OAuth authorization URL.
    
    **Returns:**
    ```json
    {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
    }
    ```
    
    **Usage:**
    1. Frontend calls this endpoint
    2. Frontend redirects user to the returned `auth_url`
    3. User authorizes on Google
    4. Google redirects back to `/auth/google/callback`
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
        )
    
    oauth_client = get_google_oauth_client()
    auth_url = oauth_client.get_authorization_url()
    
    return GoogleAuthUrlResponse(auth_url=auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(None),
    state: str = Query(None)
):
    """
    Handle Google OAuth callback.
    
    **Query Parameters:**
    - code: Authorization code from Google
    - state: Optional state parameter for CSRF protection
    
    **Flow:**
    1. Google redirects here after user authorization with 'code'
    2. Backend exchanges code for user info
    3. Backend creates/finds user in database
    4. Backend redirects to frontend with access token in URL fragment
    
    **Returns:**
    - Redirect to frontend with access_token in URL fragment
    """
    try:
        # Get frontend URL from settings
        frontend_url = settings.FRONTEND_URL
        
        if not code:
            # Redirect to frontend login page with error
            return RedirectResponse(
                url=f"{frontend_url}/login?error=no_code",
                status_code=status.HTTP_302_FOUND
            )
        
        # Exchange code for user info
        oauth_client = get_google_oauth_client()
        user_info = await oauth_client.authenticate_with_code(code)
        
        if not user_info:
            # Redirect to frontend login page with error
            return RedirectResponse(
                url=f"{frontend_url}/login?error=auth_failed",
                status_code=status.HTTP_302_FOUND
            )
        
        # Extract user information
        email = user_info.get("email")
        google_id = user_info.get("id")
        full_name = user_info.get("name")
        picture = user_info.get("picture")
        
        if not email:
            # Redirect to frontend login page with error
            return RedirectResponse(
                url=f"{frontend_url}/login?error=no_email",
                status_code=status.HTTP_302_FOUND
            )
        
        # Create or get user
        user = await create_google_user(
            email=email,
            google_id=google_id,
            full_name=full_name,
            picture=picture,
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Redirect to frontend with token in URL fragment (hash)
        # Using fragment (#) instead of query (?) keeps token out of server logs
        redirect_url = f"{frontend_url}/auth/callback#access_token={access_token}&token_type=bearer"
        
        return RedirectResponse(
            url=redirect_url,
            status_code=status.HTTP_302_FOUND
        )
    
    except HTTPException as e:
        # Redirect to frontend login page with error
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=http_error",
            status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        # Redirect to frontend login page with error
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=server_error",
            status_code=status.HTTP_302_FOUND
        )


@router.get("/callback", response_class=HTMLResponse)
async def auth_callback():
    """
    OAuth callback handler - displays HTML page that extracts token from URL hash.
    This is a fallback for when frontend doesn't handle the callback.
    
    **Returns:**
    HTML page that extracts access_token from URL hash and redirects to frontend
    """
    frontend_url = settings.FRONTEND_URL
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Authentication Successful - Modelix</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: #000000;
        }
        .container {
            background: #ffffff;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(255,255,255,0.1);
            text-align: center;
            max-width: 400px;
            border: 2px solid #000000;
        }
        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #e0e0e0;
            border-top: 4px solid #000000;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        h1 { color: #000000; margin-bottom: 10px; }
        p { color: #333333; margin: 10px 0; }
        .success { color: #000000; font-weight: bold; }
        .error { color: #000000; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="spinner"></div>
        <h1>Authenticating...</h1>
        <p id="status">Processing your login</p>
    </div>

    <script>
        // Extract token from URL hash
        const hash = window.location.hash.substring(1);
        const params = new URLSearchParams(hash);
        const accessToken = params.get('access_token');
        const tokenType = params.get('token_type');
        const error = new URLSearchParams(window.location.search).get('error');

        const statusEl = document.getElementById('status');

        if (error) {{
            statusEl.innerHTML = '<span class="error">Authentication failed: ' + error + '</span>';
            setTimeout(() => {{
                window.location.href = '{frontend_url}/login?error=' + error;
            }}, 2000);
        }} else if (accessToken) {{
            statusEl.innerHTML = '<span class="success">✓ Login successful!</span>';
            statusEl.innerHTML += '<br><span>Redirecting to dashboard...</span>';
            
            // Redirect to frontend callback page with token in hash
            // The frontend will set the cookie on its own domain
            setTimeout(() => {{
                window.location.href = '{frontend_url}/auth/callback#access_token=' + accessToken + '&token_type=' + (tokenType || 'bearer');
            }}, 1000);
        }} else {{
            statusEl.innerHTML = '<span class="error">No token received</span>';
            setTimeout(() => {{
                window.location.href = '{frontend_url}/login';
            }}, 2000);
        }}
    </script>
</body>
</html>
    """
    return html_content


@router.post("/google/signin", response_model=TokenResponse)
async def google_signin(request: GoogleAuthRequestWithState):
    """
    Alternative Google login endpoint that returns token directly (no redirect).
    
    **Request Body:**
    ```json
    {
        "code": "google_authorization_code",
        "state": "optional_state_parameter"
    }
    ```
    
    **Returns:**
    - access_token: JWT token for authentication
    - token_type: "bearer"
    - user: User information
    
    **Usage:**
    Use this endpoint if your frontend can't handle OAuth redirects
    and prefers to handle the Google authorization code directly.
    """
    try:
        if not request.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code not provided"
            )
        
        # Exchange code for user info
        oauth_client = get_google_oauth_client()
        user_info = await oauth_client.authenticate_with_code(request.code)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate with Google"
            )
        
        # Extract user information
        email = user_info.get("email")
        google_id = user_info.get("id")
        full_name = user_info.get("name")
        picture = user_info.get("picture")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )
        
        # Create or get user
        user = await create_google_user(
            email=email,
            google_id=google_id,
            full_name=full_name,
            picture=picture,
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "picture": user.picture,
                "auth_provider": user.auth_provider,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication failed. Please try again."
        )


# ==================== LOGOUT ====================
@router.post("/logout")
async def logout():
    """
    Client-side logout - no server-side action needed for JWT.
    
    **Note:**
    Since we use stateless JWT tokens, logout is handled client-side
    by removing the token from storage. This endpoint exists for
    consistency with the API spec.
    
    **Returns:**
    - Success message
    """
    return {"message": "Logged out successfully. Please remove the token from client storage."}


# ==================== GOOGLE OAUTH STATUS ====================
@router.get("/google/status")
async def google_oauth_status():
    """
    Check Google OAuth configuration status for debugging.
    
    **Returns:**
    - Status information about Google OAuth configuration
    """
    has_client_id = bool(settings.GOOGLE_CLIENT_ID)
    has_client_secret = bool(settings.GOOGLE_CLIENT_SECRET)
    has_redirect_uri = bool(settings.GOOGLE_REDIRECT_URI)
    
    is_configured = has_client_id and has_client_secret and has_redirect_uri
    
    return {
        "configured": is_configured,
        "has_client_id": has_client_id,
        "has_client_secret": has_client_secret,
        "has_redirect_uri": has_redirect_uri,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI if has_redirect_uri else None,
        "message": "Google OAuth is properly configured" if is_configured else "Google OAuth is not fully configured"
    }


# ==================== DEBUG TOKEN ====================
@router.get("/debug-token")
async def debug_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Debug endpoint to test token validation.
    
    This will help identify authentication issues.
    
    **Authentication:**
    - Requires valid JWT token in Authorization header: `Bearer <token>`
    
    **Returns:**
    - Token validation details and user information
    """
    return {
        "valid": True,
        "message": "Token is valid and authenticated",
        "user_id": current_user.get("id"),
        "email": current_user.get("email"),
        "auth_provider": current_user.get("auth_provider"),
        "is_active": current_user.get("is_active"),
        "is_verified": current_user.get("is_verified")
    }


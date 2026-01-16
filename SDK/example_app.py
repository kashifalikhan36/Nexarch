"""
Example FastAPI application with Nexarch SDK integration
"""
from fastapi import FastAPI, HTTPException
from nexarch import NexarchSDK
import sys
import os

# Add parent directory to path to import local SDK
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create FastAPI app
app = FastAPI(
    title="Demo User Service",
    description="Example app demonstrating Nexarch SDK integration",
    version="1.0.0"
)

# Initialize Nexarch SDK
sdk = NexarchSDK(
    api_key="demo_api_key_12345",
    environment="development",
    log_file="demo_telemetry.json",
    enable_local_logs=True
)

# Attach SDK to app - this auto-injects middleware and router
sdk.init(app)

# Simulated database
users_db = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
    3: {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
}

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Demo User Service API",
        "docs": "/docs",
        "nexarch_telemetry": "/__nexarch/telemetry/stats"
    }

@app.get("/users")
def list_users():
    """List all users"""
    return {"users": list(users_db.values())}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Get a specific user by ID"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=404, 
            detail=f"User with ID {user_id} not found"
        )
    return users_db[user_id]

@app.post("/users")
def create_user(user: dict):
    """Create a new user"""
    if "name" not in user or "email" not in user:
        raise HTTPException(
            status_code=400,
            detail="Both 'name' and 'email' fields are required"
        )
    
    user_id = max(users_db.keys()) + 1
    new_user = {"id": user_id, **user}
    users_db[user_id] = new_user
    return new_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """Delete a user"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found"
        )
    
    deleted_user = users_db.pop(user_id)
    return {"message": "User deleted", "user": deleted_user}

@app.get("/error")
def trigger_error():
    """Endpoint that intentionally raises an error for testing"""
    raise ValueError("This is a test error to demonstrate error tracking")

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("Starting Demo User Service with Nexarch SDK")
    print("="*60)
    print("\nAPI Documentation: http://localhost:8000/docs")
    print("Nexarch Telemetry Stats: http://localhost:8000/__nexarch/telemetry/stats")
    print("Nexarch All Data: http://localhost:8000/__nexarch/telemetry")
    print("\nLocal telemetry file: demo_telemetry.json")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

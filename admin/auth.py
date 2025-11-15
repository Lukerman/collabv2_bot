from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from config import settings
import hashlib
import secrets
from typing import Optional


# Simple session storage (in production, use Redis or similar)
active_sessions = {}


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_session(username: str) -> str:
    """Create a session token"""
    token = secrets.token_urlsafe(32)
    active_sessions[token] = username
    return token


def get_session_user(token: str) -> Optional[str]:
    """Get username from session token"""
    return active_sessions.get(token)


def delete_session(token: str):
    """Delete a session"""
    if token in active_sessions:
        del active_sessions[token]


def verify_admin(username: str, password: str) -> bool:
    """Verify admin credentials"""
    return username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD


async def get_current_user(request: Request) -> str:
    """Get current logged-in user from session"""
    token = request.cookies.get("admin_session")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    username = get_session_user(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    return username


def require_auth(request: Request) -> bool:
    """Check if user is authenticated, redirect to login if not"""
    token = request.cookies.get("admin_session")
    if not token or not get_session_user(token):
        return False
    return True
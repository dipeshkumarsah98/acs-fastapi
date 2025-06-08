from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from setting import settings
from typing import Optional
from models import User
from sqlmodel import Session, select
from auth.database import get_session
from fastapi.responses import RedirectResponse

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Middleware to validate JWT token and return the current user.
    
    Args:
        credentials: The HTTP authorization credentials containing the JWT token
        session: Database session for user lookup
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        # Verify and decode the JWT token
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Extract user email from token
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Get user from database
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: Session = Depends(get_session)
) -> Optional[User]:
    """
    Optional middleware that returns the current user if authenticated,
    or None if not authenticated.
    
    Args:
        credentials: Optional HTTP authorization credentials
        session: Database session for user lookup
        
    Returns:
        Optional[User]: The authenticated user or None
    """
    if not credentials:
        return None
        
    try:
        return await get_current_user(credentials, session)
    except HTTPException:
        return None

async def prevent_authenticated_user(
    request: Request,
    current_user: Optional[User] = Depends(get_optional_user)
) -> None:
    """
    Middleware to prevent authenticated users from accessing certain pages.
    Redirects to home page if user is already authenticated.
    
    Args:
        request: The FastAPI request object
        current_user: Optional current user from get_optional_user
        
    Raises:
        RedirectResponse: Redirects to home page if user is authenticated
    """
    if current_user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Already authenticated",
            headers={"Location": "/"}
        ) 
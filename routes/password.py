from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from models import User
from sqlmodel import Session, select
from auth.database import get_session
from auth.password import validate_password_strength
from utils import get_password_hash, verify_password
from datetime import datetime, timedelta
from auth.jwt import create_access_token
from auth.middleware import get_current_user, prevent_authenticated_user
from auth.email import send_password_reset_email
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/password", tags=["password"])
templates = Jinja2Templates(directory="templates")

@router.get("/forgot", response_class=HTMLResponse)
async def forgot_password_page(
    request: Request,
    _: None = Depends(prevent_authenticated_user)
):
    """
    Forgot password page - only accessible to non-authenticated users.
    """
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@router.post("/forgot")
async def forgot_password(
    request: Request,
    email: str = Form(...),
    _: None = Depends(prevent_authenticated_user)
):
    """
    Handle forgot password request and send reset link.
    """
    session = next(get_session())
    
    # Find user
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        # Don't reveal if email exists or not for security
        return templates.TemplateResponse(
            "forgot_password.html",
            {
                "request": request,
                "message": "If your email is registered, you will receive a password reset link."
            }
        )
    
    # Generate reset token
    reset_token = create_access_token(
        data={"sub": user.email, "type": "password_reset"},
        expires_delta=timedelta(minutes=15)  # Token expires in 15 minutes
    )
    
    # Store reset token in user record
    user.password_reset_token = reset_token
    user.password_reset_token_expiry = datetime.now() + timedelta(minutes=15)
    session.add(user)
    session.commit()
    
    # Send reset email
    reset_link = f"{request.base_url}reset-password?token={reset_token}"
    email_sent = await send_password_reset_email(email=email, reset_link=reset_link)
    
    if not email_sent:
        return templates.TemplateResponse(
            "forgot_password.html",
            {
                "request": request,
                "error": "Failed to send reset email. Please try again."
            }
        )
    
    return templates.TemplateResponse(
        "forgot_password.html",
        {
            "request": request,
            "message": "If your email is registered, you will receive a password reset link."
        }
    )

@router.get("/reset", response_class=HTMLResponse)
async def reset_password_page(
    request: Request,
    token: str,
    _: None = Depends(prevent_authenticated_user)
):
    """
    Reset password page - only accessible to non-authenticated users with valid token.
    """
    session = next(get_session())
    
    # Find user with valid reset token
    user = session.exec(
        select(User).where(
            User.password_reset_token == token,
            User.password_reset_token_expiry > datetime.utcnow()
        )
    ).first()
    
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid or expired reset link. Please request a new one."
            }
        )
    
    return templates.TemplateResponse(
        "reset_password.html",
        {
            "request": request,
            "token": token
        }
    )

@router.post("/reset")
async def reset_password(
    request: Request,
    token: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    _: None = Depends(prevent_authenticated_user)
):
    """
    Handle password reset request.
    """
    session = next(get_session())
    
    user = session.exec(
        select(User).where(
            User.password_reset_token == token,
            User.password_reset_token_expiry > datetime.utcnow()
        )
    ).first()
    
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid or expired reset link. Please request a new one."
            }
        )
    
    # Validate passwords match
    if password != confirm_password:
        return templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request,
                "token": token,
                "error": "Passwords do not match."
            }
        )
    
    # Validate password strength
    is_valid, error_message = validate_password_strength(password)
    if not is_valid:
        return templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request,
                "token": token,
                "error": error_message
            }
        )
    
    # Update password
    user.password = get_password_hash(password)
    user.password_reset_token = None
    user.password_reset_token_expiry = None
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "message": "Password has been reset successfully. Please login with your new password."
        }
    )

@router.put("/update")
async def update_user_password(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Protected API endpoint to update user password.
    Requires current password for verification.
    """
    try:
        data = await request.json()
        current_password = data.get("current_password")
        new_password = data.get("new_password")
        
        if not current_password or not new_password:
            raise HTTPException(status_code=400, detail="Current password and new password are required")
        
        # Verify current password
        session = next(get_session())
        user = session.exec(select(User).where(User.id == current_user.id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not verify_password(current_password, user.password):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Validate new password strength
        is_valid, error_message = validate_password_strength(new_password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Update password
        user.password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        session.add(user)
        session.commit()
        
        return {"message": "Password updated successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
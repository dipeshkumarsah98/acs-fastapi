from fastapi import APIRouter, Depends, HTTPException, Request, Form, Header
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from models import User
from sqlmodel import Session, select
from auth.database import get_session
from auth.password import validate_password_strength
from utils import get_password_hash, verify_password
from datetime import datetime, timedelta
from auth.jwt import create_access_token
from typing import Optional
from auth.middleware import get_current_user, get_optional_user, prevent_authenticated_user
from auth.email import send_verification_email
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    _: None = Depends(prevent_authenticated_user)
):
    """
    Login page - only accessible to non-authenticated users.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    _: None = Depends(prevent_authenticated_user)
):
    """
    Registration page - only accessible to non-authenticated users.
    """
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/login")
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    _: None = Depends(prevent_authenticated_user)
):
    try:
        """
        Login endpoint - only accessible to non-authenticated users.
        """
        session = next(get_session())
        user = session.exec(select(User).where(User.email == email)).one_or_none()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check if email is verified
        if not user.is_email_verified:
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Please verify your email before logging in."
                }
            )
        
        # Check if account is locked
        if user.account_locked_until and user.account_locked_until > datetime.utcnow():
            remaining_time = (user.account_locked_until - datetime.utcnow()).total_seconds() / 60
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": f"Account is locked. Please try again in {int(remaining_time)} minutes."
                }
            )
        
        if not verify_password(password, user.password):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            
            # Lock account if 3 failed attempts
            if user.failed_login_attempts >= 3:
                user.account_locked_until = datetime.utcnow() + timedelta(minutes=15)
                user.failed_login_attempts = 0
                session.add(user)
                session.commit()
                return templates.TemplateResponse(
                    "login.html",
                    {
                        "request": request,
                        "error": "Account locked for 15 minutes due to multiple failed attempts."
                    }
                )
            
            session.add(user)
            session.commit()
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        session.add(user)
        session.commit()
        session.refresh(user)

        access_token = create_access_token(data={"sub": user.email})

        return JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name
                }
            }
        )
    except Exception as e:
        print("error", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register")
async def register_user(
    request: Request,
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    gender: str = Form(...),
    _: None = Depends(prevent_authenticated_user),
):
    """
    Registration endpoint - only accessible to non-authenticated users.
    """
    session = next(get_session())
    
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Email already registered"
            }
        )
    
    # Validate password strength
    is_valid, error_message = validate_password_strength(password)
    if not is_valid:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": error_message
            }
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    new_user = User(
        name=fullname,
        email=email,
        password=hashed_password,
        gender=gender,
        last_login=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # Send verification email
    email_sent = await send_verification_email(email=email, session=session)
    
    if not email_sent:
        # Delete user from database
        session.delete(new_user)
        session.commit()
        
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Email not sent. Please try again. If the problem persists, please contact support."
            }
        )
    
    # Redirect to verification page
    return RedirectResponse(url="/verify-email", status_code=303)

@router.get("/verify-email", response_class=HTMLResponse)
async def verify_email_page(
    request: Request,
    _: None = Depends(prevent_authenticated_user)
):
    """
    Email verification page - only accessible to non-authenticated users.
    """
    return templates.TemplateResponse("verify_email.html", {"request": request})

@router.post("/verify-email")
async def verify_email(
    request: Request,
    otp: str = Form(...),
    _: None = Depends(prevent_authenticated_user)
):
    """
    Verify email OTP endpoint.
    """
    session = next(get_session())
    
    # Find user with matching OTP
    user = session.exec(
        select(User).where(
            User.email_verification_otp == otp,
            User.email_verification_otp_expiry > datetime.utcnow()
        )
    ).first()
    
    if not user:
        return templates.TemplateResponse(
            "verify_email.html",
            {
                "request": request,
                "error": "Invalid or expired verification code. Please try again."
            }
        )
    
    # Mark email as verified
    user.is_email_verified = True
    user.email_verification_otp = None
    user.email_verification_otp_expiry = None
    session.add(user)
    session.commit()
    
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "message": "Email verified successfully. Please login."
        }
    )

@router.get("/resend-verification", response_class=HTMLResponse)
async def resend_verification(
    request: Request,
    _: None = Depends(prevent_authenticated_user)
):
    """
    Resend verification email endpoint.
    """
    session = next(get_session())
    
    # Get email from query parameters
    email = request.query_params.get("email")
    if not email:
        return templates.TemplateResponse(
            "verify_email.html",
            {
                "request": request,
                "error": "Email address is required."
            }
        )
    
    # Find user
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return templates.TemplateResponse(
            "verify_email.html",
            {
                "request": request,
                "error": "User not found."
            }
        )
    
    # Send new verification email
    email_sent = await send_verification_email(email=email, session=session)
    
    if not email_sent:
        return templates.TemplateResponse(
            "verify_email.html",
            {
                "request": request,
                "error": "Failed to send verification email. Please try again."
            }
        )
    
    return templates.TemplateResponse(
        "verify_email.html",
        {
            "request": request,
            "message": "Verification code has been resent to your email."
        }
    )

@router.post("/logout")
async def logout_user(authorization: Optional[str] = Header(None)):
    """
    Handle user logout.
    In a real application, you might want to blacklist the token or clear server-side sessions.
    For now, we'll just return a success response as the client will clear the token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    return JSONResponse(
        content={"message": "Successfully logged out"},
        status_code=200
    ) 
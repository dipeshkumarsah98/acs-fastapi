from fastapi import Depends, FastAPI, HTTPException, Request, Form, Header
from models import User
from sqlmodel import Session, SQLModel, select
from auth.database import engine, get_session
from auth.password import validate_password_strength
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import logging
from utils import get_password_hash, verify_password
from datetime import datetime
from auth.jwt import create_access_token
from typing import Optional
from auth.middleware import get_current_user, get_optional_user, prevent_authenticated_user

logger = logging.getLogger(__name__)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):

    return templates.TemplateResponse(
        request=request, name="index.html", context={"id": id}
    )

@app.get("/protected-route")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.name}!"}

@app.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    _: None = Depends(prevent_authenticated_user)
):
    """
    Login page - only accessible to non-authenticated users.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    _: None = Depends(prevent_authenticated_user)
):
    """
    Registration page - only accessible to non-authenticated users.
    """
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/login")
async def login_user(
    email: str = Form(...),
    password: str = Form(...),
    _: None = Depends(prevent_authenticated_user)
):
    """
    Login endpoint - only accessible to non-authenticated users.
    """
    session = next(get_session())
    user = session.exec(select(User).where(User.email == email)).first()
    
    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": Request,
                "error": "Invalid email or password"
            }
        )
    
    # Update last login time
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()
    
    # Create access token
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

@app.post("/register")
async def register_user(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    gender: str = Form(...),
    _: None = Depends(prevent_authenticated_user)
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
                "request": Request,
                "error": "Email already registered"
            }
        )
    
    # Validate password strength
    if not validate_password_strength(password):
        return templates.TemplateResponse(
            "register.html",
            {
                "request": Request,
                "error": "Password does not meet requirements"
            }
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    new_user = User(
        name=name,
        email=email,
        password=hashed_password,
        gender=gender,
        last_login=datetime.utcnow()
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": new_user.email})
    
    return JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "name": new_user.name
            }
        }
    )

@app.post("/logout")
async def logout_user(authorization: Optional[str] = Header(None)):
    """
    Handle user logout.
    In a real application, you might want to blacklist the token or clear server-side sessions.
    For now, we'll just return a success response as the client will clear the token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    # In a real application, you might want to:
    # 1. Validate the token
    # 2. Add it to a blacklist
    # 3. Clear any server-side sessions
    
    return JSONResponse(
        content={"message": "Successfully logged out"},
        status_code=200
    )

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Protected profile page that requires authentication.
    """
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": current_user
        }
    )

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Protected settings page that requires authentication.
    """
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "user": current_user
        }
    )

@app.get("/api/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Protected API endpoint that returns current user information.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "gender": current_user.gender,
        "last_login": current_user.last_login
    }
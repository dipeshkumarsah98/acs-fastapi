from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from models import User
from sqlmodel import Session, select
from auth.database import get_session
from auth.middleware import get_current_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["profile"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
async def profile_page(
    request: Request,
):
    """
    Profile page - requires authentication.
    """
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
        }
    )

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
):
    """
    Settings page - requires authentication.
    """
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
        }
    )

@router.get("/api/me")
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
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }

@router.put("/api/me")
async def update_user_info(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Protected API endpoint to update user information.
    Currently only supports updating name.
    """
    try:
        data = await request.json()
        new_name = data.get("name")
        
        if not new_name:
            raise HTTPException(status_code=400, detail="Name is required")
        
        # Update user in database
        session = next(get_session())
        user = session.exec(select(User).where(User.id == current_user.id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.name = new_name
        user.updated_at = datetime.utcnow()
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "gender": user.gender,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
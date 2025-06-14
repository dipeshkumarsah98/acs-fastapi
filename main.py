from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from routes import auth, password, profile
from models import User
from auth.middleware import get_current_user

logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(password.router)
app.include_router(profile.router)

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    """
    Root endpoint - serves the index page.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

@app.get("/protected-route")
async def protected_route(current_user: User = Depends(get_current_user)):
    """
    Example protected route - requires authentication.
    """
    return {"message": f"Hello {current_user.name}!"}
from fastapi import Depends, FastAPI, HTTPException, Request
from models import User
from sqlmodel import Session, SQLModel, select
from auth.database import engine, get_session
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):

    return templates.TemplateResponse(
        request=request, name="index.html", context={"id": id}
    )

@app.get("/users")
async def get_users(request:Request, session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()

    return templates.TemplateResponse(
        "users.html", {"request": request, "users": users}
    )

@app.post("/users")
async def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/{user_id}")
async def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}")
async def update_user(user_id: int, user: User, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.name is not None:
        db_user.name = user.name

    if user.email is not None:
        db_user.email = user.email

    session.commit()
    session.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}


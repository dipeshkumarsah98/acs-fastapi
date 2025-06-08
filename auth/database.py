import os

from sqlmodel import create_engine, SQLModel, Session
from setting import settings

print("Initializing database...")
print(f"Using database URL: {settings.DATABASE_URL}")

if not settings.DATABASE_URL:
    print("DATABASE_URL is not set")
    raise ValueError("DATABASE_URL is not set")

engine = create_engine(settings.DATABASE_URL, echo=True)

SQLModel.metadata.create_all(engine)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
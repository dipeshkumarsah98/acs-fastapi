from sqlmodel import SQLModel, Field, create_engine, Session, Relationship
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    name: str
    email: str
    password: str
    gender: str
    last_login: Optional[datetime] = Field(default=datetime.now(), nullable=True)

from sqlmodel import SQLModel, Field, create_engine, Session, Relationship
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    name: str
    email: str
    password: str

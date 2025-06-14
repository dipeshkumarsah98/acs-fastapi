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
    created_at: Optional[datetime] = Field(default=datetime.now(), nullable=True)
    updated_at: Optional[datetime] = Field(default=datetime.now(), nullable=True)
    
    # Email verification fields
    is_email_verified: bool = Field(default=False)
    email_verification_otp: Optional[str] = Field(default=None, nullable=True)
    email_verification_otp_expiry: Optional[datetime] = Field(default=None, nullable=True)
    
    # Account locking fields
    failed_login_attempts: int = Field(default=0)
    account_locked_until: Optional[datetime] = Field(default=None, nullable=True)
    
    # 2FA fields
    is_2fa_enabled: bool = Field(default=False)
    two_factor_otp: Optional[str] = Field(default=None, nullable=True)
    two_factor_otp_expiry: Optional[datetime] = Field(default=None, nullable=True)
    
    # Password reset fields
    password_reset_token: Optional[str] = Field(default=None, nullable=True)
    password_reset_token_expiry: Optional[datetime] = Field(default=None, nullable=True)

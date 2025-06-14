from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import Optional
import random
from setting import settings
import string
from datetime import datetime, timedelta
from models import User
from sqlmodel import Session, select
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

def generate_otp(length: int = 6) -> str:
    """Generate a random OTP of specified length."""
    return ''.join(random.choices(string.digits, k=length))

def get_email_config() -> ConnectionConfig:
    """Get email configuration from settings."""
    return ConnectionConfig(
        MAIL_USERNAME=settings.EMAIL_USERNAME,
        MAIL_PASSWORD=settings.EMAIL_PASSWORD,
        MAIL_FROM=settings.EMAIL_FROM,
        MAIL_PORT=settings.EMAIL_PORT,
        MAIL_SERVER=settings.EMAIL_SERVER,
        MAIL_STARTTLS = True,
        MAIL_SSL_TLS = False,
        USE_CREDENTIALS = True,
        VALIDATE_CERTS = True
    )

async def send_verification_email(email: EmailStr, session: Session) -> bool:
    """Send verification email with OTP."""
    try:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            return False

        # Generate OTP
        otp = generate_otp()
        expiry = datetime.now() + timedelta(minutes=15)

        logger.info(f"Sending verification email to {email} with OTP {otp}")

        # Update user with OTP
        user.email_verification_otp = otp
        user.email_verification_otp_expiry = expiry
        session.add(user)
        session.commit()

        # Prepare email
        message = MessageSchema(
            subject="Verify Your Email",
            recipients=[email],
            body=f"""
            <html>
                <body>
                    <h2>Email Verification</h2>
                    <p>Your verification code is: <strong>{otp}</strong></p>
                    <p>This code will expire in 15 minutes.</p>
                </body>
            </html>
            """,
            subtype=MessageType.html
        )

        # Send email
        fm = FastMail(get_email_config())
        await fm.send_message(message)
        return True

    except Exception as e:
        logger.error(f"Error sending verification email:", e)
        return False

async def send_2fa_email(email: EmailStr, session: Session) -> bool:
    """Send 2FA verification email with OTP."""
    try:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            return False

        # Generate OTP
        otp = generate_otp()
        expiry = datetime.now() + timedelta(minutes=5)

        # Update user with 2FA OTP
        user.two_factor_otp = otp
        user.two_factor_otp_expiry = expiry
        session.add(user)
        session.commit()

        # Prepare email
        message = MessageSchema(
            subject="Two-Factor Authentication Code",
            recipients=[email],
            body=f"""
            <html>
                <body>
                    <h2>Two-Factor Authentication</h2>
                    <p>Your verification code is: <strong>{otp}</strong></p>
                    <p>This code will expire in 5 minutes.</p>
                </body>
            </html>
            """,
            subtype="html"
        )

        # Send email
        fm = FastMail(get_email_config())
        await fm.send_message(message)
        return True

    except Exception as e:
        logger.error(f"Error sending 2FA email: {str(e)}")
        return False

async def send_password_reset_email(email: EmailStr, reset_link: str) -> bool:
    """Send password reset email with reset link."""
    try:
        logger.info(f"Sending password reset email to {email}")

        # Prepare email
        message = MessageSchema(
            subject="Reset Your Password",
            recipients=[email],
            body=f"""
            <html>
                <body>
                    <h2>Password Reset Request</h2>
                    <p>You have requested to reset your password. Click the link below to reset your password:</p>
                    <p><a href="{reset_link}" style="display: inline-block; padding: 10px 20px; background-color: #4F46E5; color: white; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
                    <p>If you did not request this password reset, please ignore this email.</p>
                    <p>This link will expire in 15 minutes.</p>
                </body>
            </html>
            """,
            subtype=MessageType.html
        )

        # Send email
        fm = FastMail(get_email_config())
        await fm.send_message(message)
        return True

    except Exception as e:
        logger.error(f"Error sending password reset email:", e)
        return False 
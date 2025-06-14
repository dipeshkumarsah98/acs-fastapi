import re
from typing import Tuple

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    Returns a tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)"
    
    return True, "Password is valid"

def contains_personal_info(password: str, email: str = "", username: str = "") -> bool:
    """Checks if password contains parts of email or username."""
    if not email and not username:
        return False
    
    email_parts = email.split('@')[0].lower() if email else ""
    username_lower = username.lower() if username else ""
    password_lower = password.lower()
    
    return (email_parts and email_parts in password_lower) or \
           (username_lower and username_lower in password_lower) 
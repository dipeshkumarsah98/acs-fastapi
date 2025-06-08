import re
from typing import Tuple

def validate_password_strength(password: str, email: str = "", username: str = "") -> Tuple[bool, str]:
    """
    Validates password strength against multiple criteria.
    Returns a tuple of (is_valid, error_message).
    """
    # Length check
    if not (12 <= len(password) <= 16):
        return False, "Password must be between 12 and 16 characters long"

    # Character type checks
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    # Sequential character check
    sequential_patterns = [
        r'123|234|345|456|567|678|789|012',
        r'abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz'
    ]
    for pattern in sequential_patterns:
        if re.search(pattern, password.lower()):
            return False, "Password contains sequential characters"

    # Repetitive character check
    if re.search(r'(.)\1{2,}', password):
        return False, "Password contains repetitive characters"

    # Personal information check
    if contains_personal_info(password, email, username):
        return False, "Password contains personal information (name or email)"

    return True, ""

def contains_personal_info(password: str, email: str = "", username: str = "") -> bool:
    """Checks if password contains parts of email or username."""
    if not email and not username:
        return False
    
    email_parts = email.split('@')[0].lower() if email else ""
    username_lower = username.lower() if username else ""
    password_lower = password.lower()
    
    return (email_parts and email_parts in password_lower) or \
           (username_lower and username_lower in password_lower) 

import requests
from setting import settings

async def verify_recaptcha_token(recaptcha_token: str):
    """
    Verify recaptcha token
    """
    if not settings.RECAPTCHA_SECRET_KEY:
        print("RECAPTCHA_SECRET_KEY is not set")
        return False

    url = "https://www.google.com/recaptcha/api/siteverify"

    data = {
        "secret": settings.RECAPTCHA_SECRET_KEY,
        "response": recaptcha_token,
    }

    response = requests.post(url, data=data)
    data = response.json()

    return data["success"] == True

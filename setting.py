from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str = "your-secret-key-here"  # In production, set this via environment variable
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""  # Google App Password
    EMAIL_FROM: str = ""
    EMAIL_PORT: int = 587
    EMAIL_SERVER: str = "smtp.gmail.com"

    RECAPTCHA_SECRET_KEY: str = None

settings = Settings()
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB_NAME: str = "email_summarizer"

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    ENCRYPTION_KEY: str

    # The public URL of this backend server (e.g., from ngrok)
    PUBLIC_SERVER_URL: str
    # The URL of the frontend application
    FRONTEND_URL: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
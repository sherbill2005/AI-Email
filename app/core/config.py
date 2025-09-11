from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB_NAME: str = "email_summarizer"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

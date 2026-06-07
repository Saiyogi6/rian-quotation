import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Rian Studioz Quotation Engine"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./rian_studioz.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "rian-studioz-super-secret-key-change-in-prod")
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    PDF_OUTPUT_DIR: str = os.getenv("PDF_OUTPUT_DIR", "app/static/pdfs")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "rianstudioz123")
    
    class Config:
        env_file = ".env"

settings = Settings()

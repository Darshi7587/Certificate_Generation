import os
from pathlib import Path
from dotenv import load_dotenv

# Find root directory .env file
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = os.getenv("APP_NAME", "Bulk Certificate Generator API")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./certificates.db")
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "generated_certificates")


settings = Settings()

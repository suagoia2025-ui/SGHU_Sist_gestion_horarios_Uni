from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://sghu_user:sghu_pass@localhost:5432/sghu"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "SGHU - Sistema de Gestión de Horarios Universitarios"
    VERSION: str = "0.1.0"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


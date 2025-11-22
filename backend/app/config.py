from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://sghu_user:sghu_pass@localhost:5433/sghu"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "SGHU - Sistema de Gestión de Horarios Universitarios"
    VERSION: str = "0.1.0"
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Schedule Solver
    SCHEDULE_SOLVER_TIMEOUT: float = 30.0  # Timeout en segundos para el solver de horarios
    
    # API Limits
    MAX_SECTIONS_PER_QUERY: int = 1000  # Límite máximo de secciones por consulta
    MAX_SUBJECTS_PER_QUERY: int = 100   # Límite máximo de asignaturas por consulta
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


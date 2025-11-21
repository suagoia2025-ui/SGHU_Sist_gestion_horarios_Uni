"""
Dependencies para FastAPI (get_db, etc.)
"""
from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos.
    Se cierra automáticamente después de la request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""
Endpoints para horarios (placeholder para FASE 5)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db

router = APIRouter()


@router.get("/health")
def schedules_health():
    """
    Health check para módulo de horarios
    """
    return {"status": "ok", "message": "Módulo de horarios - Pendiente implementación en FASE 5"}


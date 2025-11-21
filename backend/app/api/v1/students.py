"""
Endpoints para estudiantes
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.student_service import StudentService
from app.schemas.student import StudentRead, AcademicHistoryRead, FinancialStatusRead

router = APIRouter()


@router.get("/{student_id}", response_model=StudentRead)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene información de un estudiante por ID
    """
    service = StudentService(db)
    return service.get_student(student_id)


@router.get("", response_model=List[StudentRead])
def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    program_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """
    Lista estudiantes con paginación.
    Opcionalmente filtra por programa.
    """
    service = StudentService(db)
    if program_id:
        return service.get_students_by_program(program_id, skip=skip, limit=limit)
    return service.get_students(skip=skip, limit=limit)


@router.get("/{student_id}/academic-history", response_model=List[AcademicHistoryRead])
def get_academic_history(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial académico de un estudiante
    """
    service = StudentService(db)
    return service.get_academic_history(student_id)


@router.get("/{student_id}/financial-status", response_model=FinancialStatusRead)
def get_financial_status(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado financiero de un estudiante
    """
    service = StudentService(db)
    status = service.get_financial_status(student_id)
    if not status:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Estado financiero", student_id)
    return status


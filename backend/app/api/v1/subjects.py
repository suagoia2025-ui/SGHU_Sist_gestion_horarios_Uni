"""
Endpoints para asignaturas y programas
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.subject_service import (
    SubjectService,
    ProgramService,
    CourseSectionService,
    AcademicPeriodService
)
from app.schemas.subject import SubjectRead, ProgramRead, SubjectWithPrerequisites
from app.schemas.schedule import CourseSectionRead, AcademicPeriodRead

router = APIRouter()


# Endpoints de Programas
@router.get("/programs", response_model=List[ProgramRead])
def get_programs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Lista todos los programas académicos
    """
    service = ProgramService(db)
    return service.get_programs(skip=skip, limit=limit)


@router.get("/programs/{program_id}", response_model=ProgramRead)
def get_program(
    program_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un programa por ID
    """
    service = ProgramService(db)
    return service.get_program(program_id)


# Endpoints de Asignaturas
@router.get("/subjects", response_model=List[SubjectRead])
def get_subjects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    program_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Lista asignaturas con filtros opcionales.
    Puede filtrar por programa.
    """
    service = SubjectService(db)
    return service.get_subjects(skip=skip, limit=limit, program_id=program_id)


@router.get("/subjects/{subject_id}", response_model=SubjectRead)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una asignatura por ID
    """
    service = SubjectService(db)
    return service.get_subject(subject_id)


@router.get("/subjects/{subject_id}/with-prerequisites", response_model=SubjectWithPrerequisites)
def get_subject_with_prerequisites(
    subject_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una asignatura con sus prerrequisitos
    """
    service = SubjectService(db)
    return service.get_subject_with_prerequisites(subject_id)


# Endpoints de Secciones
@router.get("/course-sections", response_model=List[CourseSectionRead])
def get_course_sections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    period_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Lista secciones de cursos con filtros opcionales.
    Puede filtrar por período y/o asignatura.
    """
    service = CourseSectionService(db)
    return service.get_sections(skip=skip, limit=limit, period_id=period_id, subject_id=subject_id)


@router.get("/course-sections/{section_id}", response_model=CourseSectionRead)
def get_course_section(
    section_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una sección con todos sus detalles (horarios, profesor, aula, etc.)
    """
    service = CourseSectionService(db)
    return service.get_section(section_id)


# Endpoints de Períodos Académicos
@router.get("/academic-periods/current", response_model=AcademicPeriodRead)
def get_current_academic_period(
    db: Session = Depends(get_db)
):
    """
    Obtiene el período académico activo
    """
    service = AcademicPeriodService(db)
    period = service.get_current_period()
    if not period:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Período académico activo", 0)
    return period


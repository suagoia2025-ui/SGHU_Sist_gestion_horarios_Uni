"""
Endpoints para generación de horarios
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.schedule_service import ScheduleService
from app.schemas.schedule import (
    ScheduleGenerationRequest,
    ScheduleSolutionResponse,
    UnassignedSubjectInfo
)
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter()


@router.post("/generate", response_model=ScheduleSolutionResponse)
def generate_schedule(
    request: ScheduleGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Genera horario para estudiante usando solo restricciones duras.
    
    El sistema intenta asignar secciones de las asignaturas seleccionadas
    respetando:
    - Sin choques de horario
    - Cupos disponibles
    - Sin conflictos de profesor/aula
    - Una sección por asignatura
    - Prerrequisitos cumplidos
    
    Body:
    {
        "student_id": 1,
        "selected_subject_ids": [1, 2, 3, 4, 5],
        "academic_period_id": 1  // Opcional, usa el activo si no se proporciona
    }
    """
    try:
        service = ScheduleService(db)
        solution = service.generate_schedule_for_student(
            student_id=request.student_id,
            selected_subject_ids=request.selected_subject_ids,
            academic_period_id=request.academic_period_id
        )
        
        return ScheduleSolutionResponse(
            student_id=solution.student_id,
            is_feasible=solution.is_feasible,
            assigned_section_ids=solution.assigned_section_ids,
            assigned_subject_ids=solution.assigned_subject_ids,
            unassigned_subjects=[
                UnassignedSubjectInfo(
                    subject_id=u.subject_id,
                    subject_code=u.subject_code,
                    subject_name=u.subject_name,
                    reason=u.reason,
                    conflicting_sections=u.conflicting_sections
                )
                for u in solution.unassigned_subjects
            ],
            processing_time=solution.processing_time,
            conflicts=solution.conflicts,
            solver_status=solution.solver_status
        )
    except NotFoundError as e:
        raise e
    except ValidationError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando horario: {str(e)}"
        )


@router.get("/health")
def schedules_health():
    """
    Health check para módulo de horarios
    """
    return {
        "status": "ok",
        "message": "Módulo de horarios - FASE 5 implementada",
        "features": [
            "Constraint Solver (OR-Tools CP-SAT)",
            "Restricciones duras implementadas",
            "Generación de horarios viables"
        ]
    }

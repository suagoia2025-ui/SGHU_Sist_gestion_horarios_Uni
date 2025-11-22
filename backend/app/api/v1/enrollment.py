"""
Endpoints para matrícula y validaciones
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.enrollment_service import EnrollmentService
from app.services.student_service import StudentService
from app.services.subject_service import SubjectService, AcademicPeriodService
from app.services.validation_service import ValidationService
from app.schemas.enrollment import EnrollmentRead
from app.schemas.validation import (
    EnrollmentRequest,
    EnrollmentValidationResult,
    SubjectEligibilityInfo,
    EnrollmentStatusResponse
)
from app.models.source.student_data import GradeStatus
from app.config import settings

router = APIRouter()


@router.post("/validate", response_model=EnrollmentValidationResult)
def validate_enrollment(
    request: EnrollmentRequest,
    db: Session = Depends(get_db)
):
    """
    Valida una solicitud de matrícula sin persistirla.
    Retorna todas las validaciones ejecutadas.
    
    Ejecuta las siguientes validaciones:
    - Estado financiero
    - Prerrequisitos
    - Límite de créditos
    - Cupos disponibles
    - Choques de horario
    - Matrículas duplicadas
    """
    service = EnrollmentService(db)
    return service.validate_enrollment_request(request)


@router.get("/{enrollment_id}", response_model=EnrollmentRead)
def get_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una matrícula por ID
    """
    service = EnrollmentService(db)
    return service.get_enrollment(enrollment_id)


@router.get("/students/{student_id}/enrollments", response_model=List[EnrollmentRead])
def get_student_enrollments(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las matrículas de un estudiante
    """
    service = EnrollmentService(db)
    return service.get_enrollments_by_student(student_id)


@router.get("/students/{student_id}/eligible-subjects", response_model=List[SubjectEligibilityInfo])
def get_eligible_subjects(
    student_id: int,
    academic_period_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Retorna asignaturas que el estudiante puede cursar.
    Incluye información de prerrequisitos cumplidos/faltantes.
    
    Si no se proporciona academic_period_id, usa el período activo.
    """
    validation_service = ValidationService(db)
    subject_service = SubjectService(db)
    period_service = AcademicPeriodService(db)
    
    # Obtener período académico
    if academic_period_id:
        period = period_service.get_period(academic_period_id)
    else:
        period = period_service.get_current_period()
        if not period:
            raise HTTPException(
                status_code=404,
                detail="No hay período académico activo"
            )
        academic_period_id = period.id
    
    # Obtener todas las asignaturas del programa del estudiante
    student_service = StudentService(db)
    try:
        student = student_service.get_student(student_id)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Estudiante con ID {student_id} no encontrado"
        )
    
    # Obtener asignaturas del programa
    all_subjects = subject_service.get_subjects(program_id=student.program_id, limit=settings.MAX_SUBJECTS_PER_QUERY)
    
    # Obtener historial académico
    academic_history = student_service.get_academic_history(student_id)
    approved_subject_ids = {h.subject_id for h in academic_history if h.status == GradeStatus.APROBADO.value}
    
    # Obtener secciones disponibles del período
    from app.repositories.subject_repository import CourseSectionRepository
    section_repo = CourseSectionRepository(db)
    available_sections = section_repo.get_by_period(academic_period_id, skip=0, limit=settings.MAX_SECTIONS_PER_QUERY)
    available_subject_ids = {s.subject_id for s in available_sections}
    
    eligible_subjects = []
    
    for subject in all_subjects:
        # Solo considerar asignaturas que tienen secciones disponibles
        if subject.id not in available_subject_ids:
            continue
        
        # Validar prerrequisitos
        prereq_validation = validation_service.validate_prerequisites(
            student_id=student_id,
            subject_id=subject.id
        )
        
        # Obtener prerrequisitos de la asignatura
        subject_with_prereqs = subject_service.get_subject_with_prerequisites(subject.id)
        prerequisites_met = []
        prerequisites_missing = []
        prerequisite_names_missing = []
        
        if subject_with_prereqs.prerequisites:
            for prereq in subject_with_prereqs.prerequisites:
                if prereq.prerequisite_subject_id in approved_subject_ids:
                    prerequisites_met.append(prereq.prerequisite_subject_id)
                else:
                    prerequisites_missing.append(prereq.prerequisite_subject_id)
                    # Obtener nombre del prerrequisito
                    try:
                        prereq_subject = subject_service.get_subject(prereq.prerequisite_subject_id)
                        prerequisite_names_missing.append(prereq_subject.name)
                    except Exception:
                        prerequisite_names_missing.append(f"Asignatura ID {prereq.prerequisite_subject_id}")
        
        # Verificar si puede matricularse
        can_enroll = prereq_validation.is_valid and subject.id not in approved_subject_ids
        reason = None
        if not prereq_validation.is_valid:
            reason = prereq_validation.message
        elif subject.id in approved_subject_ids:
            reason = "Ya aprobaste esta asignatura"
        
        eligible_subjects.append(SubjectEligibilityInfo(
            subject_id=subject.id,
            subject_code=subject.code,
            subject_name=subject.name,
            credits=subject.credits,
            is_eligible=prereq_validation.is_valid,
            prerequisites_met=prerequisites_met,
            prerequisites_missing=prerequisites_missing,
            prerequisite_names_missing=prerequisite_names_missing,
            can_enroll=can_enroll,
            reason=reason
        ))
    
    return eligible_subjects


@router.get("/students/{student_id}/enrollment-status", response_model=EnrollmentStatusResponse)
def get_enrollment_status(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Estado actual de matrícula del estudiante.
    Indica si puede matricularse, razones de bloqueo, etc.
    """
    validation_service = ValidationService(db)
    student_service = StudentService(db)
    enrollment_service = EnrollmentService(db)
    
    # Verificar que el estudiante existe
    try:
        student = student_service.get_student(student_id)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Estudiante con ID {student_id} no encontrado"
        )
    
    # Verificar estado financiero
    financial_validation = validation_service.validate_financial_status(student_id)
    financial_status = student_service.get_financial_status(student_id)
    
    financial_blocked = not financial_validation.is_valid
    financial_debt_amount = None
    financial_message = None
    
    if financial_status:
        financial_debt_amount = float(financial_status.debt_amount) if financial_status.has_debt == 'true' else None
        financial_message = financial_validation.message
    
    # Obtener materias elegibles
    try:
        eligible_subjects = get_eligible_subjects(student_id, None, db)
        eligible_count = len([s for s in eligible_subjects if s.can_enroll])
    except:
        eligible_count = 0
    
    # Obtener matrículas actuales
    enrollments = enrollment_service.get_enrollments_by_student(student_id)
    current_enrollments_count = len(enrollments)
    
    # Generar warnings y errors
    warnings = []
    errors = []
    
    if financial_blocked:
        errors.append(financial_message or "Tienes una deuda pendiente")
    
    if eligible_count == 0:
        warnings.append("No hay asignaturas elegibles disponibles en este momento")
    
    can_enroll = not financial_blocked and eligible_count > 0
    
    return EnrollmentStatusResponse(
        student_id=student_id,
        can_enroll=can_enroll,
        financial_blocked=financial_blocked,
        financial_debt_amount=financial_debt_amount,
        financial_message=financial_message,
        eligible_subjects_count=eligible_count,
        current_enrollments_count=current_enrollments_count,
        warnings=warnings,
        errors=errors
    )

"""
Service para lógica de negocio de matrícula
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.subject_repository import CourseSectionRepository
from app.repositories.student_repository import StudentRepository
from app.services.validation_service import ValidationService
from app.schemas.enrollment import EnrollmentRead
from app.schemas.validation import (
    EnrollmentValidationResult,
    ValidationResult,
    EnrollmentRequest
)


class EnrollmentService:
    """Service para operaciones con matrículas"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = EnrollmentRepository(db)
        self.validation_service = ValidationService(db)
        self.section_repo = CourseSectionRepository(db)
        self.student_repo = StudentRepository(db)
    
    def get_enrollments_by_student(self, student_id: int) -> List[EnrollmentRead]:
        """Obtiene matrículas de un estudiante"""
        enrollments = self.repository.get_by_student(student_id)
        return [EnrollmentRead.model_validate(e) for e in enrollments]
    
    def get_enrollment(self, enrollment_id: int) -> EnrollmentRead:
        """Obtiene una matrícula por ID"""
        enrollment = self.repository.get_by_id_or_404(enrollment_id)
        return EnrollmentRead.model_validate(enrollment)
    
    def validate_enrollment_request(
        self,
        request: EnrollmentRequest
    ) -> EnrollmentValidationResult:
        """
        Ejecuta todas las validaciones necesarias para una solicitud de matrícula.
        Retorna resultado consolidado.
        """
        student_id = request.student_id
        section_ids = request.section_ids
        
        validations: List[ValidationResult] = []
        
        # 0. Verificar que el estudiante existe
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return EnrollmentValidationResult(
                is_valid=False,
                can_proceed=False,
                validations=[],
                error_summary=f"Estudiante con ID {student_id} no encontrado"
            )
        
        # 1. Validar estado financiero (crítico - bloquea todo)
        financial_validation = self.validation_service.validate_financial_status(student_id)
        validations.append(financial_validation)
        
        if not financial_validation.is_valid:
            # Si hay bloqueo financiero, no continuar con otras validaciones
            return EnrollmentValidationResult(
                is_valid=False,
                can_proceed=False,
                validations=validations,
                error_summary=f"Bloqueo financiero: {financial_validation.message}"
            )
        
        # 2. Obtener subject_ids de las secciones seleccionadas
        sections = [self.section_repo.get_by_id(sid) for sid in section_ids]
        sections = [s for s in sections if s is not None]  # Filtrar None
        
        if not sections:
            return EnrollmentValidationResult(
                is_valid=False,
                can_proceed=False,
                validations=validations,
                error_summary="No se encontraron secciones válidas"
            )
        
        selected_subject_ids = [s.subject_id for s in sections]
        
        # Validar que haya al menos una sección válida
        if not selected_subject_ids:
            return EnrollmentValidationResult(
                is_valid=False,
                can_proceed=False,
                validations=validations,
                error_summary="No se encontraron secciones válidas o todas las secciones fueron filtradas"
            )
        
        # 3. Validar prerrequisitos para cada asignatura ÚNICA (no por sección)
        unique_subject_ids = list(set(selected_subject_ids))
        for subject_id in unique_subject_ids:
            prereq_validation = self.validation_service.validate_prerequisites(
                student_id=student_id,
                subject_id=subject_id,
                selected_subject_ids=selected_subject_ids
            )
            validations.append(prereq_validation)
        
        # 4. Validar cupos de cada sección
        for section_id in section_ids:
            capacity_validation = self.validation_service.validate_section_capacity(section_id)
            validations.append(capacity_validation)
        
        # 5. Validar límite de créditos
        credit_validation = self.validation_service.validate_credit_limit(
            student_id=student_id,
            selected_subject_ids=selected_subject_ids
        )
        validations.append(credit_validation)
        
        # 6. Validar choques de horario
        conflict_validation = self.validation_service.validate_schedule_conflicts(section_ids)
        validations.append(conflict_validation)
        
        # 7. Validar matrículas duplicadas para cada asignatura ÚNICA (no por sección)
        for subject_id in unique_subject_ids:
            duplicate_validation = self.validation_service.validate_duplicate_enrollment(
                student_id=student_id,
                subject_id=subject_id
            )
            validations.append(duplicate_validation)
        
        # Consolidar resultados
        all_valid = all(v.is_valid for v in validations)
        
        # Determinar si puede proceder (todos los críticos deben pasar)
        critical_validations = [
            v for v in validations
            if v.validation_type in [
                "financial_status",
                "prerequisites",
                "credit_limit",
                "section_capacity",
                "schedule_conflicts"
            ]
        ]
        can_proceed = all(v.is_valid for v in critical_validations)
        
        # Generar resumen de errores
        failed_validations = [v for v in validations if not v.is_valid]
        error_summary = None
        if failed_validations:
            error_messages = [v.message for v in failed_validations]
            error_summary = "; ".join(error_messages)
        
        return EnrollmentValidationResult(
            is_valid=all_valid,
            can_proceed=can_proceed,
            validations=validations,
            error_summary=error_summary
        )

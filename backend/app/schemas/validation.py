"""
Schemas Pydantic para validaciones de matrícula
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ValidationResult(BaseModel):
    """Resultado individual de una validación"""
    validation_type: str
    is_valid: bool
    message: str
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class EnrollmentRequest(BaseModel):
    """Petición de matrícula"""
    student_id: int
    academic_period_id: int
    section_ids: List[int]


class EnrollmentValidationResult(BaseModel):
    """Resultado consolidado de todas las validaciones"""
    is_valid: bool
    can_proceed: bool
    validations: List[ValidationResult]
    error_summary: Optional[str] = None

    class Config:
        from_attributes = True


class SubjectEligibilityInfo(BaseModel):
    """Información de elegibilidad de una asignatura"""
    subject_id: int
    subject_code: str
    subject_name: str
    credits: int
    is_eligible: bool
    prerequisites_met: List[int]  # IDs de prerrequisitos cumplidos
    prerequisites_missing: List[int]  # IDs de prerrequisitos faltantes
    prerequisite_names_missing: List[str]  # Nombres de prerrequisitos faltantes
    can_enroll: bool
    reason: Optional[str] = None  # Razón si no puede matricularse

    class Config:
        from_attributes = True


class EnrollmentStatusResponse(BaseModel):
    """Estado de matrícula de un estudiante"""
    student_id: int
    can_enroll: bool
    financial_blocked: bool
    financial_debt_amount: Optional[float] = None
    financial_message: Optional[str] = None
    eligible_subjects_count: int
    current_enrollments_count: int
    warnings: List[str] = []
    errors: List[str] = []

    class Config:
        from_attributes = True


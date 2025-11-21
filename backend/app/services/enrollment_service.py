"""
Service para lógica de negocio de matrícula (básico)
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.enrollment_repository import EnrollmentRepository
from app.schemas.enrollment import EnrollmentRead


class EnrollmentService:
    """Service para operaciones con matrículas (versión básica)"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = EnrollmentRepository(db)
    
    def get_enrollments_by_student(self, student_id: int) -> List[EnrollmentRead]:
        """Obtiene matrículas de un estudiante"""
        enrollments = self.repository.get_by_student(student_id)
        return [EnrollmentRead.model_validate(e) for e in enrollments]
    
    def get_enrollment(self, enrollment_id: int) -> EnrollmentRead:
        """Obtiene una matrícula por ID"""
        enrollment = self.repository.get_by_id_or_404(enrollment_id)
        return EnrollmentRead.model_validate(enrollment)


"""
Service para lógica de negocio de estudiantes
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.student_repository import StudentRepository
from app.schemas.student import StudentRead, AcademicHistoryRead, FinancialStatusRead
from app.models.source.people import Student


class StudentService:
    """Service para operaciones con estudiantes"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = StudentRepository(db)
    
    def get_student(self, student_id: int) -> StudentRead:
        """Obtiene un estudiante por ID"""
        student = self.repository.get_with_program(student_id)
        if not student:
            from app.core.exceptions import NotFoundError
            raise NotFoundError("Estudiante", student_id)
        return StudentRead.model_validate(student)
    
    def get_students(self, skip: int = 0, limit: int = 100) -> List[StudentRead]:
        """Obtiene lista de estudiantes"""
        students = self.repository.get_all(skip=skip, limit=limit)
        return [StudentRead.model_validate(s) for s in students]
    
    def get_students_by_program(self, program_id: int, skip: int = 0, limit: int = 100) -> List[StudentRead]:
        """Obtiene estudiantes de un programa"""
        students = self.repository.get_by_program(program_id, skip=skip, limit=limit)
        return [StudentRead.model_validate(s) for s in students]
    
    def get_academic_history(self, student_id: int) -> List[AcademicHistoryRead]:
        """Obtiene historial académico de un estudiante"""
        history = self.repository.get_academic_history(student_id)
        return [AcademicHistoryRead.model_validate(h) for h in history]
    
    def get_financial_status(self, student_id: int) -> Optional[FinancialStatusRead]:
        """Obtiene estado financiero de un estudiante"""
        status = self.repository.get_financial_status(student_id)
        if not status:
            return None
        return FinancialStatusRead.model_validate(status)


"""
Repository para estudiantes
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.repositories.base import BaseRepository
from app.models.source.people import Student
from app.models.source.academic import Program
from app.models.source.student_data import AcademicHistory, FinancialStatus


class StudentRepository(BaseRepository[Student]):
    """Repository para operaciones con estudiantes"""
    
    def __init__(self, db: Session):
        super().__init__(db, Student)
    
    def get_by_code(self, code: str) -> Optional[Student]:
        """Obtiene estudiante por código"""
        return self.db.query(Student).filter(Student.code == code).first()
    
    def get_with_program(self, student_id: int) -> Optional[Student]:
        """Obtiene estudiante con información del programa"""
        return self.db.query(Student).options(
            joinedload(Student.program)
        ).filter(Student.id == student_id).first()
    
    def get_academic_history(self, student_id: int) -> List[AcademicHistory]:
        """Obtiene historial académico de un estudiante"""
        return self.db.query(AcademicHistory).filter(
            AcademicHistory.student_id == student_id
        ).order_by(AcademicHistory.period).all()
    
    def get_financial_status(self, student_id: int) -> Optional[FinancialStatus]:
        """Obtiene estado financiero de un estudiante"""
        return self.db.query(FinancialStatus).filter(
            FinancialStatus.student_id == student_id
        ).first()
    
    def get_by_program(self, program_id: int, skip: int = 0, limit: int = 100) -> List[Student]:
        """Obtiene estudiantes de un programa"""
        return self.db.query(Student).filter(
            Student.program_id == program_id
        ).offset(skip).limit(limit).all()


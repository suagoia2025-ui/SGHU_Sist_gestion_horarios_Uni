"""
Repository para matrículas
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.sghu.enrollment import StudentEnrollment, EnrollmentSubject, EnrollmentPeriod


class EnrollmentRepository(BaseRepository[StudentEnrollment]):
    """Repository para operaciones con matrículas"""
    
    def __init__(self, db: Session):
        super().__init__(db, StudentEnrollment)
    
    def get_by_student(self, student_id: int) -> List[StudentEnrollment]:
        """Obtiene matrículas de un estudiante"""
        return self.db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == student_id
        ).order_by(StudentEnrollment.created_at.desc()).all()
    
    def get_by_period(self, period_id: int) -> List[StudentEnrollment]:
        """Obtiene matrículas de un período"""
        return self.db.query(StudentEnrollment).filter(
            StudentEnrollment.enrollment_period_id == period_id
        ).all()


class EnrollmentPeriodRepository(BaseRepository[EnrollmentPeriod]):
    """Repository para períodos de matrícula"""
    
    def __init__(self, db: Session):
        super().__init__(db, EnrollmentPeriod)
    
    def get_active(self) -> Optional[EnrollmentPeriod]:
        """Obtiene el período de matrícula activo"""
        return self.db.query(EnrollmentPeriod).filter(
            EnrollmentPeriod.status == 'open'
        ).first()


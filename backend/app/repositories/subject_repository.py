"""
Repository para asignaturas y programas
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.repositories.base import BaseRepository
from app.models.source.academic import Subject, Program, Prerequisite
from app.models.source.offer import CourseSection, AcademicPeriod


class SubjectRepository(BaseRepository[Subject]):
    """Repository para operaciones con asignaturas"""
    
    def __init__(self, db: Session):
        super().__init__(db, Subject)
    
    def get_by_code(self, code: str) -> Optional[Subject]:
        """Obtiene asignatura por código"""
        return self.db.query(Subject).filter(Subject.code == code).first()
    
    def get_by_program(self, program_id: int, skip: int = 0, limit: int = 100) -> List[Subject]:
        """Obtiene asignaturas de un programa"""
        return self.db.query(Subject).filter(
            Subject.program_id == program_id
        ).offset(skip).limit(limit).all()
    
    def get_with_prerequisites(self, subject_id: int) -> Optional[Subject]:
        """Obtiene asignatura con sus prerrequisitos"""
        return self.db.query(Subject).options(
            joinedload(Subject.prerequisites)
        ).filter(Subject.id == subject_id).first()


class ProgramRepository(BaseRepository[Program]):
    """Repository para operaciones con programas"""
    
    def __init__(self, db: Session):
        super().__init__(db, Program)
    
    def get_by_code(self, code: str) -> Optional[Program]:
        """Obtiene programa por código"""
        return self.db.query(Program).filter(Program.code == code).first()


class CourseSectionRepository(BaseRepository[CourseSection]):
    """Repository para operaciones con secciones"""
    
    def __init__(self, db: Session):
        super().__init__(db, CourseSection)
    
    def get_by_period(self, period_id: int, skip: int = 0, limit: int = 100) -> List[CourseSection]:
        """Obtiene secciones de un período"""
        return self.db.query(CourseSection).filter(
            CourseSection.period_id == period_id
        ).offset(skip).limit(limit).all()
    
    def get_with_details(self, section_id: int) -> Optional[CourseSection]:
        """Obtiene sección con todas sus relaciones"""
        return self.db.query(CourseSection).options(
            joinedload(CourseSection.period),
            joinedload(CourseSection.subject),
            joinedload(CourseSection.professor),
            joinedload(CourseSection.classroom),
            joinedload(CourseSection.section_schedules)
        ).filter(CourseSection.id == section_id).first()
    
    def get_by_subject(self, subject_id: int, period_id: Optional[int] = None) -> List[CourseSection]:
        """Obtiene secciones de una asignatura"""
        query = self.db.query(CourseSection).filter(
            CourseSection.subject_id == subject_id
        )
        if period_id:
            query = query.filter(CourseSection.period_id == period_id)
        return query.all()


class AcademicPeriodRepository(BaseRepository[AcademicPeriod]):
    """Repository para operaciones con períodos académicos"""
    
    def __init__(self, db: Session):
        super().__init__(db, AcademicPeriod)
    
    def get_current(self) -> Optional[AcademicPeriod]:
        """Obtiene el período académico activo"""
        return self.db.query(AcademicPeriod).filter(
            AcademicPeriod.status == 'active'
        ).first()
    
    def get_by_code(self, code: str) -> Optional[AcademicPeriod]:
        """Obtiene período por código"""
        return self.db.query(AcademicPeriod).filter(
            AcademicPeriod.code == code
        ).first()


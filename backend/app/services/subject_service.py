"""
Service para lógica de negocio de asignaturas y oferta académica
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.subject_repository import (
    SubjectRepository,
    ProgramRepository,
    CourseSectionRepository,
    AcademicPeriodRepository
)
from app.schemas.subject import SubjectRead, ProgramRead, SubjectWithPrerequisites
from app.schemas.schedule import CourseSectionRead, AcademicPeriodRead


class SubjectService:
    """Service para operaciones con asignaturas"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = SubjectRepository(db)
    
    def get_subject(self, subject_id: int) -> SubjectRead:
        """Obtiene una asignatura por ID"""
        subject = self.repository.get_by_id_or_404(subject_id)
        return SubjectRead.model_validate(subject)
    
    def get_subjects(self, skip: int = 0, limit: int = 100, program_id: Optional[int] = None) -> List[SubjectRead]:
        """Obtiene lista de asignaturas con filtros opcionales"""
        if program_id:
            subjects = self.repository.get_by_program(program_id, skip=skip, limit=limit)
        else:
            subjects = self.repository.get_all(skip=skip, limit=limit)
        return [SubjectRead.model_validate(s) for s in subjects]
    
    def get_subject_with_prerequisites(self, subject_id: int) -> SubjectWithPrerequisites:
        """Obtiene asignatura con sus prerrequisitos"""
        subject = self.repository.get_with_prerequisites(subject_id)
        if not subject:
            from app.core.exceptions import NotFoundError
            raise NotFoundError("Asignatura", subject_id)
        return SubjectWithPrerequisites.model_validate(subject)


class ProgramService:
    """Service para operaciones con programas"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = ProgramRepository(db)
    
    def get_programs(self, skip: int = 0, limit: int = 100) -> List[ProgramRead]:
        """Obtiene lista de programas"""
        programs = self.repository.get_all(skip=skip, limit=limit)
        return [ProgramRead.model_validate(p) for p in programs]
    
    def get_program(self, program_id: int) -> ProgramRead:
        """Obtiene un programa por ID"""
        program = self.repository.get_by_id_or_404(program_id)
        return ProgramRead.model_validate(program)


class CourseSectionService:
    """Service para operaciones con secciones"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = CourseSectionRepository(db)
    
    def get_section(self, section_id: int) -> CourseSectionRead:
        """Obtiene una sección con todos sus detalles"""
        section = self.repository.get_with_details(section_id)
        if not section:
            from app.core.exceptions import NotFoundError
            raise NotFoundError("Sección", section_id)
        return CourseSectionRead.model_validate(section)
    
    def get_sections(
        self,
        skip: int = 0,
        limit: int = 100,
        period_id: Optional[int] = None,
        subject_id: Optional[int] = None
    ) -> List[CourseSectionRead]:
        """Obtiene lista de secciones con filtros opcionales"""
        if subject_id:
            sections = self.repository.get_by_subject(subject_id, period_id)
        elif period_id:
            sections = self.repository.get_by_period(period_id, skip=skip, limit=limit)
        else:
            sections = self.repository.get_all(skip=skip, limit=limit)
        
        # Cargar relaciones para cada sección
        result = []
        for section in sections:
            section_with_details = self.repository.get_with_details(section.id)
            if section_with_details:
                result.append(CourseSectionRead.model_validate(section_with_details))
        return result


class AcademicPeriodService:
    """Service para operaciones con períodos académicos"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = AcademicPeriodRepository(db)
    
    def get_current_period(self) -> Optional[AcademicPeriodRead]:
        """Obtiene el período académico activo"""
        period = self.repository.get_current()
        if not period:
            return None
        return AcademicPeriodRead.model_validate(period)
    
    def get_period(self, period_id: int) -> AcademicPeriodRead:
        """Obtiene un período por ID"""
        period = self.repository.get_by_id_or_404(period_id)
        return AcademicPeriodRead.model_validate(period)


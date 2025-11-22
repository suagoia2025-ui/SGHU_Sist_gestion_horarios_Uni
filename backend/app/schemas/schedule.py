"""
Schemas Pydantic para horarios y secciones
"""
from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional, List


class AcademicPeriodRead(BaseModel):
    """Schema para lectura de período académico"""
    id: int
    code: str
    name: str
    start_date: date
    end_date: date
    enrollment_start: date
    enrollment_end: date
    status: str

    class Config:
        from_attributes = True


class SectionScheduleRead(BaseModel):
    """Schema para lectura de horario de sección"""
    id: int
    section_id: int
    day_of_week: int
    start_time: time
    end_time: time
    session_type: str

    class Config:
        from_attributes = True


class ProfessorRead(BaseModel):
    """Schema para lectura de profesor"""
    id: int
    code: str
    first_name: str
    last_name: str
    email: str
    department: str
    specialty: Optional[str] = None

    class Config:
        from_attributes = True


class ClassroomRead(BaseModel):
    """Schema para lectura de aula"""
    id: int
    code: str
    building: str
    floor: int
    capacity: int
    type: str

    class Config:
        from_attributes = True


class SubjectBasicRead(BaseModel):
    """Schema básico para asignatura en sección"""
    id: int
    code: str
    name: str
    credits: int

    class Config:
        from_attributes = True


class CourseSectionRead(BaseModel):
    """Schema para lectura de sección con relaciones"""
    id: int
    period_id: int
    subject_id: int
    section_number: int
    professor_id: int
    capacity: int
    enrolled_count: int
    classroom_id: int
    period: Optional[AcademicPeriodRead] = None
    subject: Optional[SubjectBasicRead] = None
    professor: Optional[ProfessorRead] = None
    classroom: Optional[ClassroomRead] = None
    section_schedules: Optional[List[SectionScheduleRead]] = []

    class Config:
        from_attributes = True


class ScheduleSlotRead(BaseModel):
    """Schema para lectura de slot de horario generado"""
    id: int
    schedule_id: int
    section_id: int
    day_of_week: int
    start_time: time
    end_time: time

    class Config:
        from_attributes = True


class GeneratedScheduleRead(BaseModel):
    """Schema para lectura de horario generado"""
    id: int
    enrollment_id: int
    generation_method: str
    quality_score: Optional[float] = None
    processing_time: Optional[float] = None
    status: str
    created_at: datetime
    schedule_slots: Optional[List[ScheduleSlotRead]] = []

    class Config:
        from_attributes = True


class ScheduleGenerationRequest(BaseModel):
    """Petición para generar horario"""
    student_id: int
    selected_subject_ids: List[int]
    academic_period_id: Optional[int] = None


class UnassignedSubjectInfo(BaseModel):
    """Información sobre asignatura no asignada"""
    subject_id: int
    subject_code: str
    subject_name: str
    reason: str
    conflicting_sections: List[dict]


class ScheduleSolutionResponse(BaseModel):
    """Respuesta de generación de horario"""
    student_id: int
    is_feasible: bool
    assigned_section_ids: List[int]
    assigned_subject_ids: List[int]
    unassigned_subjects: List[UnassignedSubjectInfo]
    processing_time: float
    conflicts: List[str]
    solver_status: str

    class Config:
        from_attributes = True


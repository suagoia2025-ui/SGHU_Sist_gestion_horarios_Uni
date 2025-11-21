"""
Schemas Pydantic para asignaturas y programas
"""
from pydantic import BaseModel
from typing import Optional, List


class SubjectBase(BaseModel):
    """Schema base para asignatura"""
    code: str
    name: str
    credits: int
    theory_hours: int
    practice_hours: int
    lab_hours: int
    program_id: int


class SubjectRead(SubjectBase):
    """Schema para lectura de asignatura"""
    id: int

    class Config:
        from_attributes = True


class PrerequisiteRead(BaseModel):
    """Schema para lectura de prerrequisito"""
    id: int
    subject_id: int
    prerequisite_subject_id: int
    type: str

    class Config:
        from_attributes = True


class SubjectWithPrerequisites(SubjectRead):
    """Schema para asignatura con prerrequisitos"""
    prerequisites: Optional[List[PrerequisiteRead]] = []

    class Config:
        from_attributes = True


class ProgramRead(BaseModel):
    """Schema para lectura de programa"""
    id: int
    code: str
    name: str
    faculty: str
    credits_required: int
    duration_semesters: int

    class Config:
        from_attributes = True


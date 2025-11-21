"""
Schemas Pydantic para matrícula
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class EnrollmentCreate(BaseModel):
    """Schema para crear matrícula"""
    student_id: int
    academic_period_id: int
    section_ids: List[int]


class EnrollmentRead(BaseModel):
    """Schema para lectura de matrícula"""
    id: int
    enrollment_period_id: int
    student_id: int
    total_credits: int
    status: str
    created_at: datetime
    confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EnrollmentSubjectRead(BaseModel):
    """Schema para lectura de asignatura en matrícula"""
    id: int
    enrollment_id: int
    section_id: int
    status: str

    class Config:
        from_attributes = True


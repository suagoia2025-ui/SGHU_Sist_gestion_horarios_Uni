"""
Schemas Pydantic para estudiantes
"""
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional


class ProgramBase(BaseModel):
    """Schema base para programa"""
    code: str
    name: str
    faculty: str


class ProgramRead(ProgramBase):
    """Schema para lectura de programa"""
    id: int
    credits_required: int
    duration_semesters: int

    class Config:
        from_attributes = True


class StudentBase(BaseModel):
    """Schema base para estudiante"""
    code: str
    first_name: str
    last_name: str
    email: EmailStr
    program_id: int
    current_semester: int
    admission_date: date


class StudentCreate(StudentBase):
    """Schema para crear estudiante"""
    pass


class StudentRead(StudentBase):
    """Schema para lectura de estudiante"""
    id: int
    program: Optional[ProgramRead] = None

    class Config:
        from_attributes = True


class AcademicHistoryBase(BaseModel):
    """Schema base para historial académico"""
    subject_id: int
    period: str
    grade: Optional[float] = None
    status: str
    credits_earned: int


class AcademicHistoryRead(AcademicHistoryBase):
    """Schema para lectura de historial académico"""
    id: int
    student_id: int

    class Config:
        from_attributes = True


class FinancialStatusRead(BaseModel):
    """Schema para lectura de estado financiero"""
    id: int
    student_id: int
    has_debt: str
    debt_amount: float
    payment_status: str
    last_updated: date

    class Config:
        from_attributes = True


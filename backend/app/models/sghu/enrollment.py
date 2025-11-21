"""
Modelos de matrícula del esquema "sghu"
- EnrollmentPeriods: Control de períodos de matrícula
- StudentEnrollments: Matrículas de estudiantes
- EnrollmentSubjects: Asignaturas por matrícula
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class EnrollmentPeriod(Base):
    """Control de períodos de matrícula"""
    __tablename__ = "enrollment_periods"
    __table_args__ = {"schema": "sghu"}

    id = Column(Integer, primary_key=True, index=True)
    academic_period_id = Column(Integer, ForeignKey("source.academic_periods.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # 'open', 'closed', 'pending'
    opened_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    # Relationships
    academic_period = relationship("AcademicPeriod", back_populates="enrollment_periods")
    student_enrollments = relationship("StudentEnrollment", back_populates="enrollment_period")


class StudentEnrollment(Base):
    """Matrículas de estudiantes"""
    __tablename__ = "student_enrollments"
    __table_args__ = {"schema": "sghu"}

    id = Column(Integer, primary_key=True, index=True)
    enrollment_period_id = Column(Integer, ForeignKey("sghu.enrollment_periods.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("source.students.id"), nullable=False, index=True)
    total_credits = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)  # 'pending', 'confirmed', 'rejected', 'cancelled'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    confirmed_at = Column(DateTime, nullable=True)

    # Relationships
    enrollment_period = relationship("EnrollmentPeriod", back_populates="student_enrollments")
    student = relationship("Student", back_populates="student_enrollments")
    enrollment_subjects = relationship("EnrollmentSubject", back_populates="enrollment")
    generated_schedules = relationship("GeneratedSchedule", back_populates="enrollment")
    processing_logs = relationship("ProcessingLog", back_populates="enrollment")


class EnrollmentSubject(Base):
    """Asignaturas por matrícula"""
    __tablename__ = "enrollment_subjects"
    __table_args__ = {"schema": "sghu"}

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("sghu.student_enrollments.id"), nullable=False, index=True)
    section_id = Column(Integer, ForeignKey("source.course_sections.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # 'pendiente', 'confirmado', 'rechazado'

    # Relationships
    enrollment = relationship("StudentEnrollment", back_populates="enrollment_subjects")
    section = relationship("CourseSection", back_populates="enrollment_subjects")


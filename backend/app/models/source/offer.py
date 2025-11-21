"""
Modelos de oferta académica del esquema "source"
- AcademicPeriods: Períodos académicos
- CourseSections: Secciones ofertadas
- SectionSchedules: Horarios de secciones
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PeriodStatus(str, enum.Enum):
    """Estados de período académico"""
    PLANNING = "planning"
    ACTIVE = "active"
    CLOSED = "closed"


class AcademicPeriod(Base):
    """Períodos académicos"""
    __tablename__ = "academic_periods"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    enrollment_start = Column(Date, nullable=False)
    enrollment_end = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="planning")

    # Relationships
    course_sections = relationship("CourseSection", back_populates="period")
    enrollment_periods = relationship("EnrollmentPeriod", back_populates="academic_period")


class CourseSection(Base):
    """Secciones ofertadas"""
    __tablename__ = "course_sections"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    period_id = Column(Integer, ForeignKey("source.academic_periods.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("source.subjects.id"), nullable=False)
    section_number = Column(Integer, nullable=False)
    professor_id = Column(Integer, ForeignKey("source.professors.id"), nullable=False)
    capacity = Column(Integer, nullable=False)
    enrolled_count = Column(Integer, default=0, nullable=False)
    classroom_id = Column(Integer, ForeignKey("source.classrooms.id"), nullable=False)

    # Relationships
    period = relationship("AcademicPeriod", back_populates="course_sections")
    subject = relationship("Subject", back_populates="course_sections")
    professor = relationship("Professor", back_populates="course_sections")
    classroom = relationship("Classroom", back_populates="course_sections")
    section_schedules = relationship("SectionSchedule", back_populates="section")
    enrollment_subjects = relationship("EnrollmentSubject", back_populates="section")
    schedule_slots = relationship("ScheduleSlot", back_populates="section")
    moodle_courses = relationship("MoodleCourse", back_populates="section")


class SectionSchedule(Base):
    """Horarios de secciones"""
    __tablename__ = "section_schedules"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("source.course_sections.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Lunes, 6=Domingo
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    session_type = Column(String(20), nullable=False)  # 'teoría', 'práctica', 'laboratorio'

    # Relationships
    section = relationship("CourseSection", back_populates="section_schedules")


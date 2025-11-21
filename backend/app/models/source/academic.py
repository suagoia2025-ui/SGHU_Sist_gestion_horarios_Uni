"""
Modelos académicos del esquema "source"
- Programs: Programas académicos
- Subjects: Catálogo de asignaturas
- Prerequisites: Red de prerrequisitos
- StudyPlans: Malla curricular
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from app.database import Base


class Program(Base):
    """Programas académicos (Ingeniería, Medicina, etc.)"""
    __tablename__ = "programs"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    faculty = Column(String(100), nullable=False)
    credits_required = Column(Integer, nullable=False)
    duration_semesters = Column(Integer, nullable=False)

    # Relationships
    subjects = relationship("Subject", back_populates="program")
    students = relationship("Student", back_populates="program")
    study_plans = relationship("StudyPlan", back_populates="program")


class Subject(Base):
    """Catálogo de asignaturas"""
    __tablename__ = "subjects"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    credits = Column(Integer, nullable=False)
    theory_hours = Column(Integer, default=0)
    practice_hours = Column(Integer, default=0)
    lab_hours = Column(Integer, default=0)
    program_id = Column(Integer, ForeignKey("source.programs.id"), nullable=False)

    # Relationships
    program = relationship("Program", back_populates="subjects")
    prerequisites = relationship(
        "Prerequisite",
        foreign_keys="Prerequisite.subject_id",
        back_populates="subject"
    )
    prerequisite_for = relationship(
        "Prerequisite",
        foreign_keys="Prerequisite.prerequisite_subject_id",
        back_populates="prerequisite_subject"
    )
    study_plans = relationship("StudyPlan", back_populates="subject")
    course_sections = relationship("CourseSection", back_populates="subject")
    academic_history = relationship("AcademicHistory", back_populates="subject")


class Prerequisite(Base):
    """Red de prerrequisitos entre asignaturas"""
    __tablename__ = "prerequisites"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("source.subjects.id"), nullable=False)
    prerequisite_subject_id = Column(Integer, ForeignKey("source.subjects.id"), nullable=False)
    type = Column(String(20), nullable=False)  # 'obligatorio' o 'correquisito'

    # Relationships
    subject = relationship("Subject", foreign_keys=[subject_id], back_populates="prerequisites")
    prerequisite_subject = relationship("Subject", foreign_keys=[prerequisite_subject_id], back_populates="prerequisite_for")


class StudyPlan(Base):
    """Malla curricular"""
    __tablename__ = "study_plans"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("source.programs.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("source.subjects.id"), nullable=False)
    semester = Column(Integer, nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)

    # Relationships
    program = relationship("Program", back_populates="study_plans")
    subject = relationship("Subject", back_populates="study_plans")


"""
Modelos de personas del esquema "source"
- Professors: Docentes
- Students: Datos personales de estudiantes
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Professor(Base):
    """Docentes"""
    __tablename__ = "professors"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    department = Column(String(100), nullable=False)
    specialty = Column(String(200))

    # Relationships
    course_sections = relationship("CourseSection", back_populates="professor")


class Student(Base):
    """Datos personales de estudiantes"""
    __tablename__ = "students"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    program_id = Column(Integer, ForeignKey("source.programs.id"), nullable=False)
    current_semester = Column(Integer, nullable=False)
    admission_date = Column(Date, nullable=False)

    # Relationships
    program = relationship("Program", back_populates="students")
    academic_history = relationship("AcademicHistory", back_populates="student")
    financial_status = relationship("FinancialStatus", back_populates="student", uselist=False)
    student_enrollments = relationship("StudentEnrollment", back_populates="student")
    moodle_enrollments = relationship("MoodleEnrollment", back_populates="student")


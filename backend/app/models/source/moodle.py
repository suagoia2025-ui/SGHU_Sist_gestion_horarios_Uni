"""
Modelos de Moodle (simulación LMS) del esquema "source"
- MoodleCourses: Cursos en Moodle
- MoodleEnrollments: Inscripciones en Moodle
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base


class MoodleCourse(Base):
    """Cursos en Moodle"""
    __tablename__ = "moodle_courses"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(50), nullable=False, index=True)
    course_name = Column(String(200), nullable=False)
    section_id = Column(Integer, ForeignKey("source.course_sections.id"), nullable=False)
    moodle_id = Column(Integer, unique=True, nullable=True, index=True)
    created_at = Column(Date, nullable=False)

    # Relationships
    section = relationship("CourseSection", back_populates="moodle_courses")
    enrollments = relationship("MoodleEnrollment", back_populates="moodle_course")


class MoodleEnrollment(Base):
    """Inscripciones en Moodle"""
    __tablename__ = "moodle_enrollments"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    moodle_course_id = Column(Integer, ForeignKey("source.moodle_courses.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("source.students.id"), nullable=False)
    role = Column(String(50), nullable=False)  # 'student', 'teacher', 'assistant'
    enrollment_date = Column(Date, nullable=False)

    # Relationships
    moodle_course = relationship("MoodleCourse", back_populates="enrollments")
    student = relationship("Student", back_populates="moodle_enrollments")


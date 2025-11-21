"""
Modelos de infraestructura del esquema "source"
- Classrooms: Aulas
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Classroom(Base):
    """Aulas"""
    __tablename__ = "classrooms"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    building = Column(String(100), nullable=False)
    floor = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    type = Column(String(50), nullable=False)  # 'laboratorio', 'aula', 'auditorio'

    # Relationships
    course_sections = relationship("CourseSection", back_populates="classroom")


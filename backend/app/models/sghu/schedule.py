"""
Modelos de horarios del esquema "sghu"
- GeneratedSchedules: Horarios generados
- ScheduleSlots: Bloques de horario
- ScheduleConflicts: Conflictos detectados
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Time, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class GeneratedSchedule(Base):
    """Horarios generados por el sistema"""
    __tablename__ = "generated_schedules"
    __table_args__ = {"schema": "sghu"}

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("sghu.student_enrollments.id"), nullable=False, index=True)
    generation_method = Column(String(50), nullable=False)  # 'constraint_solver', 'genetic', 'hybrid'
    quality_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)  # en segundos
    status = Column(String(20), nullable=False)  # 'pending', 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    enrollment = relationship("StudentEnrollment", back_populates="generated_schedules")
    schedule_slots = relationship("ScheduleSlot", back_populates="schedule")
    schedule_conflicts = relationship("ScheduleConflict", back_populates="schedule")


class ScheduleSlot(Base):
    """Bloques de horario asignados"""
    __tablename__ = "schedule_slots"
    __table_args__ = {"schema": "sghu"}

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("sghu.generated_schedules.id"), nullable=False, index=True)
    section_id = Column(Integer, ForeignKey("source.course_sections.id"), nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Lunes, 6=Domingo
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # Relationships
    schedule = relationship("GeneratedSchedule", back_populates="schedule_slots")
    section = relationship("CourseSection", back_populates="schedule_slots")


class ScheduleConflict(Base):
    """Conflictos detectados en horarios"""
    __tablename__ = "schedule_conflicts"
    __table_args__ = {"schema": "sghu"}

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("sghu.generated_schedules.id"), nullable=False, index=True)
    conflict_type = Column(String(50), nullable=False)  # 'time_overlap', 'capacity', 'prerequisite', etc.
    description = Column(String(500), nullable=False)
    severity = Column(String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    resolved = Column(Boolean, default=False, nullable=False)

    # Relationships
    schedule = relationship("GeneratedSchedule", back_populates="schedule_conflicts")


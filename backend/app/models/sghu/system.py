"""
Modelos de sistema del esquema "sghu"
- ProcessingLogs: Logs de ejecución
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class ProcessingLog(Base):
    """Logs de ejecución de procesos"""
    __tablename__ = "processing_logs"
    __table_args__ = {"schema": "sghu"}

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("sghu.student_enrollments.id"), nullable=True, index=True)
    process_type = Column(String(50), nullable=False)  # 'enrollment', 'schedule_generation', 'validation'
    status = Column(String(20), nullable=False)  # 'started', 'completed', 'failed'
    message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    error_details = Column(Text, nullable=True)

    # Relationships
    enrollment = relationship("StudentEnrollment", back_populates="processing_logs")


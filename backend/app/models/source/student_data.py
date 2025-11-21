"""
Modelos de datos de estudiantes del esquema "source"
- AcademicHistory: Historial académico
- FinancialStatus: Estado financiero
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class GradeStatus(str, enum.Enum):
    """Estados de calificación"""
    APROBADO = "aprobado"
    REPROBADO = "reprobado"
    CURSANDO = "cursando"


class AcademicHistory(Base):
    """Historial académico de estudiantes"""
    __tablename__ = "academic_history"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("source.students.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("source.subjects.id"), nullable=False, index=True)
    period = Column(String(20), nullable=False)  # Ej: "2025-1"
    grade = Column(Float, nullable=True)  # 0.0 - 5.0
    status = Column(String(20), nullable=False)  # 'aprobado', 'reprobado', 'cursando'
    credits_earned = Column(Integer, default=0, nullable=False)

    # Relationships
    student = relationship("Student", back_populates="academic_history")
    subject = relationship("Subject", back_populates="academic_history")


class FinancialStatus(Base):
    """Estado financiero de estudiantes"""
    __tablename__ = "financial_status"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("source.students.id"), unique=True, nullable=False, index=True)
    has_debt = Column(String(10), default="false", nullable=False)  # 'true' o 'false'
    debt_amount = Column(Float, default=0.0, nullable=False)
    payment_status = Column(String(50), nullable=False)  # 'al día', 'pendiente', 'moroso'
    last_updated = Column(Date, nullable=False)

    # Relationships
    student = relationship("Student", back_populates="financial_status")


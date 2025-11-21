"""
Modelos de reglas académicas del esquema "source"
- AcademicRules: Reglas institucionales
"""
from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class AcademicRule(Base):
    """Reglas institucionales"""
    __tablename__ = "academic_rules"
    __table_args__ = {"schema": "source"}

    id = Column(Integer, primary_key=True, index=True)
    rule_type = Column(String(50), nullable=False, index=True)  # Ej: 'max_credits', 'min_credits'
    rule_value = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)


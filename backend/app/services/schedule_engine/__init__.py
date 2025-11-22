"""
Motor de generación de horarios usando OR-Tools (CP-SAT)
"""
from app.services.schedule_engine.models import TimeSlot, Section, Student
from app.services.schedule_engine.constraint_solver import ConstraintScheduleSolver
from app.services.schedule_engine.solution import ScheduleSolution

__all__ = [
    'TimeSlot',
    'Section',
    'Student',
    'ConstraintScheduleSolver',
    'ScheduleSolution'
]


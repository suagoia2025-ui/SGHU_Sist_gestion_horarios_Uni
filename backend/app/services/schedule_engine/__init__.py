"""
Motor de generación de horarios usando OR-Tools (CP-SAT)
"""
from app.services.schedule_engine.models import TimeSlot, Section, Student
from app.services.schedule_engine.solution import ScheduleSolution

# Importar constraint_solver solo cuando sea necesario para evitar errores si ortools no está instalado
try:
    from app.services.schedule_engine.constraint_solver import ConstraintScheduleSolver
    __all__ = [
        'TimeSlot',
        'Section',
        'Student',
        'ConstraintScheduleSolver',
        'ScheduleSolution'
    ]
except ImportError:
    # Ortools no disponible, pero no es crítico para imports básicos
    ConstraintScheduleSolver = None
    __all__ = [
        'TimeSlot',
        'Section',
        'Student',
        'ScheduleSolution'
    ]


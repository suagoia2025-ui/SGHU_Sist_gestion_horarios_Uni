"""
Modelo de solución del solver
"""
from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class UnassignedSubject:
    """Información sobre una asignatura no asignada"""
    subject_id: int
    subject_code: str
    subject_name: str
    reason: str  # Razón por la que no se asignó
    conflicting_sections: List[Dict[str, any]]  # Secciones que chocan con las asignadas


@dataclass
class ScheduleSolution:
    """Resultado de la generación de horario"""
    student_id: int
    is_feasible: bool
    assigned_section_ids: List[int]  # IDs de secciones asignadas
    assigned_subject_ids: List[int]  # IDs de asignaturas asignadas
    unassigned_subjects: List[UnassignedSubject]  # Asignaturas no asignadas y razones
    processing_time: float  # Tiempo en segundos
    conflicts: List[str]  # Lista de conflictos si no es viable
    solver_status: str  # OPTIMAL, FEASIBLE, INFEASIBLE, etc.
    quality_score: Optional[float] = None  # Score de calidad (fitness) - menor es mejor
    
    def __post_init__(self):
        """Validar datos después de inicialización"""
        if not self.is_feasible and not self.conflicts:
            self.conflicts = ["Solución infactible - razón desconocida"]
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para respuesta JSON"""
        return {
            "student_id": self.student_id,
            "is_feasible": self.is_feasible,
            "assigned_section_ids": self.assigned_section_ids,
            "assigned_subject_ids": self.assigned_subject_ids,
            "unassigned_subjects": [
                {
                    "subject_id": u.subject_id,
                    "subject_code": u.subject_code,
                    "subject_name": u.subject_name,
                    "reason": u.reason,
                    "conflicting_sections": u.conflicting_sections
                }
                for u in self.unassigned_subjects
            ],
            "processing_time": self.processing_time,
            "conflicts": self.conflicts,
            "solver_status": self.solver_status,
            "quality_score": self.quality_score
        }


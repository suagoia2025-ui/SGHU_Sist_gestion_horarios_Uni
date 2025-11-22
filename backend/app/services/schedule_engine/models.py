"""
Modelos de datos para el motor de horarios
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import time


@dataclass
class TimeSlot:
    """Representa un bloque de tiempo (día + horario)"""
    id: int
    day_of_week: int  # 0=Lunes, 1=Martes, ..., 6=Domingo
    start_time: time
    end_time: time
    
    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """
        Detecta si dos TimeSlots se solapan.
        Dos slots se solapan si:
        - Son el mismo día Y
        - Sus intervalos de tiempo se intersectan
        """
        if self.day_of_week != other.day_of_week:
            return False
        
        # Convertir time a minutos para comparar
        def time_to_minutes(t: time) -> int:
            return t.hour * 60 + t.minute
        
        start1 = time_to_minutes(self.start_time)
        end1 = time_to_minutes(self.end_time)
        start2 = time_to_minutes(other.start_time)
        end2 = time_to_minutes(other.end_time)
        
        # Se solapan si no hay separación entre ellos
        return not (end1 <= start2 or end2 <= start1)
    
    def __hash__(self):
        return hash((self.id, self.day_of_week, self.start_time, self.end_time))
    
    def __eq__(self, other):
        if not isinstance(other, TimeSlot):
            return False
        return (self.id == other.id and 
                self.day_of_week == other.day_of_week and
                self.start_time == other.start_time and
                self.end_time == other.end_time)


@dataclass
class Section:
    """Representa una sección de curso con toda su información"""
    id: int
    subject_id: int
    subject_code: str
    subject_name: str
    professor_id: int
    classroom_id: int
    capacity: int
    enrolled_count: int
    section_number: int
    timeslots: List[TimeSlot]  # Horarios de esta sección
    
    @property
    def available_spots(self) -> int:
        """Cupos disponibles"""
        return max(0, self.capacity - self.enrolled_count)
    
    def has_time_overlap_with(self, other: 'Section') -> bool:
        """Verifica si esta sección tiene choque de horario con otra"""
        for slot1 in self.timeslots:
            for slot2 in other.timeslots:
                if slot1.overlaps_with(slot2):
                    return True
        return False


@dataclass
class Student:
    """Datos del estudiante necesarios para generar horario"""
    id: int
    program_id: int
    approved_subject_ids: List[int]  # IDs de asignaturas ya aprobadas
    selected_subject_ids: List[int]  # IDs de asignaturas que quiere cursar
    
    def has_approved(self, subject_id: int) -> bool:
        """Verifica si el estudiante aprobó una asignatura"""
        return subject_id in self.approved_subject_ids


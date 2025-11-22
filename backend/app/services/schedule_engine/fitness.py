"""
Función de fitness para evaluar calidad de horarios (restricciones blandas)
"""
from typing import List
from datetime import time, timedelta
from app.services.schedule_engine.models import Section, TimeSlot


class ScheduleFitness:
    """
    Calcula el fitness (calidad) de un horario.
    Menor score = mejor horario (penalizaciones suman, bonificaciones restan)
    """
    
    def __init__(self, sections: List[Section]):
        """
        Args:
            sections: Lista de secciones asignadas en el horario
        """
        self.sections = sections
        self.slots: List[TimeSlot] = []
        for section in sections:
            self.slots.extend(section.timeslots)
    
    def calculate_fitness(self) -> float:
        """
        Calcula fitness total del horario.
        
        Returns:
            Score total (menor = mejor)
        """
        score = 0.0
        
        score += self._calculate_gaps_penalty()
        score += self._calculate_balance_penalty()
        score += self._calculate_time_preference_penalty()
        score += self._calculate_free_days_bonus()
        
        return score
    
    def _calculate_gaps_penalty(self) -> float:
        """
        Penaliza huecos entre clases del mismo día.
        
        Ejemplo:
        - Clase 7am-9am, luego clase 2pm-4pm = Gap de 5 horas (malo)
        - Clase 7am-9am, luego clase 9am-11am = Gap de 0 horas (bueno)
        
        Returns:
            Penalización (mayor = peor)
        """
        total_gap_minutes = 0
        gap_weight = 0.08  # Peso: cada minuto de gap penaliza 0.08 puntos (reducido para balancear con otros componentes)
        
        for day in range(7):  # Lunes (0) a Domingo (6)
            day_slots = [slot for slot in self.slots if slot.day_of_week == day]
            
            if len(day_slots) < 2:
                continue  # No hay gaps si hay menos de 2 clases
            
            # Ordenar por hora de inicio
            day_slots.sort(key=lambda s: s.start_time)
            
            # Calcular gaps entre clases consecutivas
            for i in range(len(day_slots) - 1):
                current_end = day_slots[i].end_time
                next_start = day_slots[i + 1].start_time
                
                # Convertir a minutos para calcular diferencia
                current_end_minutes = current_end.hour * 60 + current_end.minute
                next_start_minutes = next_start.hour * 60 + next_start.minute
                
                gap_minutes = next_start_minutes - current_end_minutes
                
                if gap_minutes > 0:
                    total_gap_minutes += gap_minutes
        
        return total_gap_minutes * gap_weight
    
    def _calculate_balance_penalty(self) -> float:
        """
        Penaliza distribución desbalanceada en la semana.
        
        Ideal: clases distribuidas uniformemente (ej: 3 días con 2 clases cada uno)
        Malo: todas las clases en 2 días
        
        Returns:
            Penalización basada en desviación estándar
        """
        classes_per_day = [0] * 7
        
        for slot in self.slots:
            classes_per_day[slot.day_of_week] += 1
        
        # Calcular desviación estándar
        mean = sum(classes_per_day) / len(classes_per_day) if classes_per_day else 0
        
        if mean == 0:
            return 0
        
        variance = sum((x - mean) ** 2 for x in classes_per_day) / len(classes_per_day)
        std_dev = variance ** 0.5
        
        balance_weight = 40.0  # Peso para desbalance (aumentado significativamente para priorizar mejor distribución)
        # Nota: Este peso alto asegura que el balance tenga suficiente impacto en el fitness total
        return std_dev * balance_weight
    
    def _calculate_time_preference_penalty(self) -> float:
        """
        Penaliza clases muy temprano o muy tarde.
        
        Preferido: 8am-6pm
        Aceptable: 7am-7pm
        No deseado: antes 7am o después 7pm
        
        Returns:
            Penalización por horarios no preferidos
        """
        penalty = 0.0
        
        for slot in self.slots:
            start_hour = slot.start_time.hour
            
            if start_hour < 7:
                # Muy temprano (antes de 7am)
                penalty += 20.0
            elif start_hour > 18:
                # Muy tarde (después de 6pm)
                penalty += 10.0
            elif start_hour < 8:
                # Temprano pero aceptable (7am-8am)
                penalty += 5.0
            elif start_hour > 17:
                # Tarde pero aceptable (5pm-6pm)
                penalty += 3.0
        
        return penalty
    
    def _calculate_free_days_bonus(self) -> float:
        """
        Bonifica tener días completamente libres.
        
        Returns:
            Bonus negativo (mejora fitness, reduce score)
        """
        days_with_classes = set()
        
        for slot in self.slots:
            days_with_classes.add(slot.day_of_week)
        
        free_days = 7 - len(days_with_classes)
        free_day_bonus = -20.0  # Cada día libre bonifica -20 (reduce score)
        
        return free_days * free_day_bonus
    
    def get_fitness_breakdown(self) -> dict:
        """
        Retorna desglose detallado del fitness para análisis.
        
        Returns:
            Diccionario con componentes del fitness
        """
        return {
            "total_fitness": self.calculate_fitness(),
            "gaps_penalty": self._calculate_gaps_penalty(),
            "balance_penalty": self._calculate_balance_penalty(),
            "time_preference_penalty": self._calculate_time_preference_penalty(),
            "free_days_bonus": self._calculate_free_days_bonus(),
            "total_slots": len(self.slots),
            "days_with_classes": len(set(slot.day_of_week for slot in self.slots))
        }


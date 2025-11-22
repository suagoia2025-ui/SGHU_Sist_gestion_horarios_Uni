"""
Motor híbrido que combina OR-Tools (restricciones duras) + Algoritmo Genético (optimización)
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.services.schedule_engine.models import Student, Section
from app.services.schedule_engine.solution import ScheduleSolution
from app.services.schedule_engine.constraint_solver import ConstraintScheduleSolver
from app.services.schedule_engine.genetic_optimizer import GeneticScheduleOptimizer

logger = logging.getLogger(__name__)


class HybridScheduleEngine:
    """
    Motor híbrido que combina Constraint Solver + Genetic Algorithm.
    
    Estrategia:
    1. Fase 1: Usar OR-Tools CP-SAT para encontrar cualquier solución viable (restricciones duras)
    2. Fase 2: Usar AG para mejorar la solución optimizando restricciones blandas
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_optimized_schedule(
        self,
        student: Student,
        available_sections: List[Section],
        optimization_level: str = "medium"
    ) -> ScheduleSolution:
        """
        Genera horario optimizado usando enfoque híbrido.
        
        Args:
            student: Datos del estudiante
            available_sections: Secciones disponibles
            optimization_level: "none" | "low" | "medium" | "high"
        
        Returns:
            ScheduleSolution con el mejor horario encontrado
        """
        import time
        start_time = time.time()
        
        # FASE 1: Encontrar solución viable con CP-SAT
        logger.info("Phase 1: Finding feasible solution with CP-SAT...")
        constraint_solver = ConstraintScheduleSolver(student, available_sections)
        constraint_solver.create_variables()
        constraint_solver.add_constraints()
        initial_solution = constraint_solver.solve()
        
        if not initial_solution.is_feasible:
            # No hay solución viable
            logger.warning("No feasible solution found with CP-SAT")
            return initial_solution
        
        # Calcular fitness de la solución inicial si no está calculado
        if initial_solution.quality_score is None:
            initial_sections = [
                s for s in available_sections 
                if s.id in initial_solution.assigned_section_ids
            ]
            from app.services.schedule_engine.fitness import ScheduleFitness
            fitness_calc = ScheduleFitness(initial_sections)
            initial_solution.quality_score = fitness_calc.calculate_fitness()
        
        logger.info(f"Phase 1 complete: Found solution with quality_score={initial_solution.quality_score:.2f}")
        
        # FASE 2: Optimizar con AG (si se solicita)
        if optimization_level == "none":
            logger.info("Skipping optimization (level=none)")
            return initial_solution
        
        logger.info(f"Phase 2: Optimizing with Genetic Algorithm (level={optimization_level})...")
        
        # Configurar parámetros según nivel
        ga_params = self._get_ga_parameters(optimization_level)
        
        genetic_optimizer = GeneticScheduleOptimizer(
            student=student,
            available_sections=available_sections,
            population_size=ga_params['population'],
            generations=ga_params['generations'],
            crossover_rate=ga_params.get('crossover_rate', 0.7),
            mutation_rate=ga_params.get('mutation_rate', 0.2)
        )
        
        optimized_solution = genetic_optimizer.optimize()
        
        # Calcular tiempo total
        total_time = time.time() - start_time
        optimized_solution.processing_time = total_time
        
        # El genetic_optimizer ya calcula assigned_subject_ids y unassigned_subjects correctamente
        # No necesitamos sobrescribirlos aquí
        
        # Comparar y retornar mejor solución
        if optimized_solution.is_feasible and optimized_solution.quality_score is not None:
            if initial_solution.quality_score is not None:
                if optimized_solution.quality_score < initial_solution.quality_score:
                    improvement = initial_solution.quality_score - optimized_solution.quality_score
                    logger.info(f"AG improved solution: {improvement:.2f} points better")
                    optimized_solution.solver_status = "HYBRID_OPTIMIZED"
                    return optimized_solution
                else:
                    logger.info("CP-SAT solution was already optimal or better")
                    initial_solution.solver_status = "HYBRID_CP_SAT_BEST"
                    return initial_solution
            else:
                # Si la solución inicial no tiene quality_score, usar la optimizada
                logger.info("Using optimized solution (initial had no quality_score)")
                optimized_solution.solver_status = "HYBRID_OPTIMIZED"
                return optimized_solution
        else:
            # Si la optimización falló, retornar solución inicial
            logger.warning("Genetic optimization failed, using CP-SAT solution")
            initial_solution.solver_status = "HYBRID_CP_SAT_FALLBACK"
            return initial_solution
    
    def _get_ga_parameters(self, level: str) -> dict:
        """
        Parámetros de AG según nivel de optimización.
        
        Args:
            level: "low" | "medium" | "high"
        
        Returns:
            Diccionario con parámetros
        """
        params = {
            "low": {
                "population": 50,
                "generations": 20,
                "crossover_rate": 0.7,
                "mutation_rate": 0.2
            },
            "medium": {
                "population": 100,
                "generations": 50,
                "crossover_rate": 0.7,
                "mutation_rate": 0.2
            },
            "high": {
                "population": 200,
                "generations": 100,
                "crossover_rate": 0.7,
                "mutation_rate": 0.2
            }
        }
        return params.get(level, params["medium"])


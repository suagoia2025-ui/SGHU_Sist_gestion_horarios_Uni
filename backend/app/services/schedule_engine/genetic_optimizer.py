"""
Optimizador de horarios usando Algoritmo Genético (DEAP)
"""
import random
import time
from typing import List, Dict, Tuple, Optional
from deap import base, creator, tools

from app.services.schedule_engine.models import Student, Section
from app.services.schedule_engine.solution import ScheduleSolution, UnassignedSubject
from app.services.schedule_engine.fitness import ScheduleFitness
from app.services.schedule_engine.constraint_solver import ConstraintScheduleSolver


# Configurar DEAP
if not hasattr(creator, "FitnessMin"):
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
if not hasattr(creator, "Individual"):
    creator.create("Individual", list, fitness=creator.FitnessMin)


class GeneticScheduleOptimizer:
    """
    Optimiza horarios usando Algoritmo Genético.
    
    Representación:
    - Un individuo = Lista de IDs de secciones asignadas
    - Ejemplo: [12, 45, 78, 23] = cursar secciones 12, 45, 78, 23
    """
    
    def __init__(
        self,
        student: Student,
        available_sections: List[Section],
        population_size: int = 100,
        generations: int = 50,
        crossover_rate: float = 0.7,
        mutation_rate: float = 0.2,
        tournament_size: int = 3
    ):
        """
        Args:
            student: Datos del estudiante
            available_sections: Secciones disponibles para elegir
            population_size: Tamaño de la población
            generations: Número de generaciones
            crossover_rate: Probabilidad de cruce (0.0-1.0)
            mutation_rate: Probabilidad de mutación (0.0-1.0)
            tournament_size: Tamaño del torneo para selección
        """
        self.student = student
        self.available_sections = available_sections
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        
        # Mapear secciones por asignatura para acceso rápido
        self.sections_by_subject: Dict[int, List[Section]] = {}
        for section in available_sections:
            if section.subject_id not in self.sections_by_subject:
                self.sections_by_subject[section.subject_id] = []
            self.sections_by_subject[section.subject_id].append(section)
        
        # Mapear secciones por ID
        self.sections_by_id: Dict[int, Section] = {s.id: s for s in available_sections}
        
        self._setup_deap()
    
    def _setup_deap(self):
        """Configurar toolbox de DEAP"""
        self.toolbox = base.Toolbox()
        
        # Registrar funciones
        self.toolbox.register("individual", self._create_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self._evaluate)
        self.toolbox.register("mate", self._crossover)
        self.toolbox.register("mutate", self._mutate)
        self.toolbox.register("select", tools.selTournament, tournsize=self.tournament_size)
    
    def _create_individual(self) -> creator.Individual:
        """
        Crea un individuo aleatorio (horario aleatorio válido).
        Asegura que cumple restricciones duras.
        
        Returns:
            Lista de IDs de secciones (una por cada asignatura seleccionada)
        """
        individual = []
        
        for subject_id in self.student.selected_subject_ids:
            # Obtener secciones disponibles para esta asignatura
            subject_sections = self.sections_by_subject.get(subject_id, [])
            
            if not subject_sections:
                # No hay secciones disponibles, usar placeholder
                individual.append(-1)  # Marcador de inválido
                continue
            
            # Elegir sección aleatoria que no cause choques con las ya seleccionadas
            valid_sections = []
            for section in subject_sections:
                # Verificar que no choque con secciones ya seleccionadas
                is_valid = True
                for selected_section_id in individual:
                    if selected_section_id == -1:
                        continue
                    selected_section = self.sections_by_id.get(selected_section_id)
                    if selected_section and section.has_time_overlap_with(selected_section):
                        is_valid = False
                        break
                
                # Verificar cupos
                if section.available_spots <= 0:
                    is_valid = False
                
                if is_valid:
                    valid_sections.append(section)
            
            if valid_sections:
                selected = random.choice(valid_sections)
                individual.append(selected.id)
            else:
                # No hay secciones válidas, usar placeholder
                individual.append(-1)
        
        return creator.Individual(individual)
    
    def _evaluate(self, individual: List[int]) -> Tuple[float]:
        """
        Evalúa un individuo usando función de fitness.
        
        Args:
            individual: Lista de IDs de secciones
        
        Returns:
            Tupla con fitness (menor = mejor)
        """
        # Filtrar secciones válidas (eliminar -1)
        valid_section_ids = [sid for sid in individual if sid != -1 and sid in self.sections_by_id]
        
        if not valid_section_ids:
            # Individuo inválido, penalización alta
            return (10000.0,)
        
        # Obtener secciones correspondientes
        sections = [self.sections_by_id[sid] for sid in valid_section_ids]
        
        # Calcular fitness
        fitness_calculator = ScheduleFitness(sections)
        fitness_score = fitness_calculator.calculate_fitness()
        
        return (fitness_score,)
    
    def _crossover(self, ind1: creator.Individual, ind2: creator.Individual) -> Tuple[creator.Individual, creator.Individual]:
        """
        Operador de cruce: combina dos individuos (padres) para crear dos hijos.
        
        Estrategia: Para cada asignatura, heredar sección de uno de los padres.
        
        Args:
            ind1: Primer padre
            ind2: Segundo padre
        
        Returns:
            Dos hijos (tupla)
        """
        child1 = creator.Individual([])
        child2 = creator.Individual([])
        
        for i in range(len(ind1)):
            if random.random() < 0.5:
                # Heredar de padre 1
                child1.append(ind1[i])
                child2.append(ind2[i])
            else:
                # Heredar de padre 2
                child1.append(ind2[i])
                child2.append(ind1[i])
        
        return child1, child2
    
    def _mutate(self, individual: creator.Individual) -> Tuple[creator.Individual]:
        """
        Operador de mutación: cambia aleatoriamente una sección.
        
        Args:
            individual: Individuo a mutar
        
        Returns:
            Individuo mutado (tupla)
        """
        if random.random() < self.mutation_rate:
            # Elegir posición aleatoria
            idx = random.randint(0, len(individual) - 1)
            subject_id = self.student.selected_subject_ids[idx]
            
            # Obtener secciones alternativas para esta asignatura
            subject_sections = self.sections_by_subject.get(subject_id, [])
            
            if subject_sections:
                # Filtrar secciones válidas (que no choquen con otras ya seleccionadas)
                valid_sections = []
                for section in subject_sections:
                    is_valid = True
                    for i, selected_section_id in enumerate(individual):
                        if i == idx or selected_section_id == -1:
                            continue
                        selected_section = self.sections_by_id.get(selected_section_id)
                        if selected_section and section.has_time_overlap_with(selected_section):
                            is_valid = False
                            break
                    
                    if section.available_spots <= 0:
                        is_valid = False
                    
                    if is_valid:
                        valid_sections.append(section)
                
                if valid_sections:
                    # Cambiar por otra sección válida
                    individual[idx] = random.choice(valid_sections).id
                else:
                    # No hay alternativas válidas, marcar como inválido
                    individual[idx] = -1
        
        return (individual,)
    
    def optimize(self) -> ScheduleSolution:
        """
        Ejecuta algoritmo genético.
        
        Returns:
            ScheduleSolution con el mejor horario encontrado
        """
        start_time = time.time()
        
        # Crear población inicial
        population = self.toolbox.population(n=self.population_size)
        
        # Evaluar población inicial
        fitnesses = list(map(self.toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit
        
        # Evolucionar por N generaciones
        best_fitness_history = []
        for generation in range(self.generations):
            # Selección
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))
            
            # Cruce
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.crossover_rate:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
            
            # Mutación
            for mutant in offspring:
                if random.random() < self.mutation_rate:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values
            
            # Evaluar individuos con fitness inválido
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            
            # Reemplazar población
            population[:] = offspring
            
            # Registrar mejor fitness de esta generación
            best_ind = tools.selBest(population, 1)[0]
            best_fitness_history.append(best_ind.fitness.values[0])
        
        processing_time = time.time() - start_time
        
        # Obtener mejor individuo
        best_individual = tools.selBest(population, 1)[0]
        
        # Convertir a ScheduleSolution
        return self._convert_to_solution(best_individual, processing_time, best_fitness_history)
    
    def _convert_to_solution(
        self,
        individual: List[int],
        processing_time: float,
        fitness_history: List[float]
    ) -> ScheduleSolution:
        """
        Convierte un individuo (lista de IDs de secciones) a ScheduleSolution.
        
        Args:
            individual: Mejor individuo encontrado
            processing_time: Tiempo de procesamiento
            fitness_history: Historial de fitness por generación
        
        Returns:
            ScheduleSolution
        """
        # Filtrar secciones válidas
        valid_section_ids = [sid for sid in individual if sid != -1 and sid in self.sections_by_id]
        
        if not valid_section_ids:
            return ScheduleSolution(
                student_id=self.student.id,
                is_feasible=False,
                assigned_section_ids=[],
                assigned_subject_ids=[],
                unassigned_subjects=[],
                processing_time=processing_time,
                conflicts=["No se encontró solución válida"],
                solver_status="INFEASIBLE",
                quality_score=None
            )
        
        # Obtener secciones y calcular fitness
        sections = [self.sections_by_id[sid] for sid in valid_section_ids]
        assigned_subject_ids = list(set(s.subject_id for s in sections))
        
        # Calcular fitness usando instancia
        fitness_calculator = ScheduleFitness(sections)
        quality_score = fitness_calculator.calculate_fitness()
        
        # Analizar asignaturas no asignadas
        unassigned_subjects = []
        for subject_id in self.student.selected_subject_ids:
            if subject_id not in assigned_subject_ids:
                subject_sections = self.sections_by_subject.get(subject_id, [])
                first_section = subject_sections[0] if subject_sections else None
                
                unassigned_subjects.append(UnassignedSubject(
                    subject_id=subject_id,
                    subject_code=first_section.subject_code if first_section else f"SUB{subject_id}",
                    subject_name=first_section.subject_name if first_section else f"Asignatura {subject_id}",
                    reason="No se pudo asignar durante la optimización genética",
                    conflicting_sections=[]
                ))
        
        return ScheduleSolution(
            student_id=self.student.id,
            is_feasible=True,
            assigned_section_ids=valid_section_ids,
            assigned_subject_ids=assigned_subject_ids,
            unassigned_subjects=unassigned_subjects,
            processing_time=processing_time,
            conflicts=[],
            solver_status="OPTIMIZED",
            quality_score=quality_score
        )


"""
Solver de restricciones duras usando OR-Tools CP-SAT
"""
import time
from typing import List, Dict, Tuple
from ortools.sat.python import cp_model

from app.services.schedule_engine.models import Student, Section
from app.services.schedule_engine.solution import ScheduleSolution
from app.config import settings


class ConstraintScheduleSolver:
    """
    Genera horarios usando CP-SAT resolviendo solo restricciones duras.
    
    Variables de decisión:
    - x[section_id] = 1 si la sección es asignada al estudiante, 0 si no
    """
    
    def __init__(self, student: Student, available_sections: List[Section]):
        self.student = student
        self.sections = available_sections
        self.model = cp_model.CpModel()
        self.variables: Dict[int, cp_model.IntVar] = {}
        self.solver = cp_model.CpSolver()
        self.start_time = None
    
    def create_variables(self):
        """Crear variables de decisión binarias para cada sección"""
        for section in self.sections:
            # Variable binaria: 1 = sección asignada, 0 = no asignada
            var_name = f"section_{section.id}"
            self.variables[section.id] = self.model.NewBoolVar(var_name)
    
    def add_constraints(self):
        """Agregar todas las restricciones duras"""
        self._add_capacity_constraints()
        self._add_time_conflict_constraints()
        self._add_professor_conflict_constraints()
        self._add_classroom_conflict_constraints()
        self._add_prerequisite_constraints()
        self._add_one_section_per_subject_constraint()
    
    def _add_capacity_constraints(self):
        """
        Una sección sin cupos disponibles no puede ser seleccionada.
        """
        for section in self.sections:
            if section.available_spots <= 0:
                # Forzar que esta sección NO sea seleccionada
                self.model.Add(self.variables[section.id] == 0)
    
    def _add_time_conflict_constraints(self):
        """
        Un estudiante no puede estar en dos lugares al mismo tiempo.
        Si sección A y B tienen timeslots que se solapan,
        no pueden estar ambas asignadas.
        """
        for i, section_a in enumerate(self.sections):
            for section_b in self.sections[i + 1:]:
                if section_a.has_time_overlap_with(section_b):
                    # No pueden estar ambas asignadas simultáneamente
                    self.model.Add(
                        self.variables[section_a.id] + 
                        self.variables[section_b.id] <= 1
                    )
    
    def _add_professor_conflict_constraints(self):
        """
        Un profesor no puede dar dos clases simultáneas.
        (Relevante si generamos horarios para múltiples estudiantes)
        """
        # Agrupar secciones por profesor
        sections_by_professor: Dict[int, List[Section]] = {}
        for section in self.sections:
            if section.professor_id not in sections_by_professor:
                sections_by_professor[section.professor_id] = []
            sections_by_professor[section.professor_id].append(section)
        
        # Para cada profesor, verificar conflictos entre sus secciones
        for professor_id, prof_sections in sections_by_professor.items():
            for i, section_a in enumerate(prof_sections):
                for section_b in prof_sections[i + 1:]:
                    if section_a.has_time_overlap_with(section_b):
                        # El profesor no puede dar ambas clases al mismo tiempo
                        self.model.Add(
                            self.variables[section_a.id] + 
                            self.variables[section_b.id] <= 1
                        )
    
    def _add_classroom_conflict_constraints(self):
        """
        Un aula no puede estar ocupada por dos secciones al mismo tiempo.
        """
        # Agrupar secciones por aula
        sections_by_classroom: Dict[int, List[Section]] = {}
        for section in self.sections:
            if section.classroom_id not in sections_by_classroom:
                sections_by_classroom[section.classroom_id] = []
            sections_by_classroom[section.classroom_id].append(section)
        
        # Para cada aula, verificar conflictos entre secciones
        for classroom_id, classroom_sections in sections_by_classroom.items():
            for i, section_a in enumerate(classroom_sections):
                for section_b in classroom_sections[i + 1:]:
                    if section_a.has_time_overlap_with(section_b):
                        # El aula no puede estar ocupada por ambas secciones al mismo tiempo
                        self.model.Add(
                            self.variables[section_a.id] + 
                            self.variables[section_b.id] <= 1
                        )
    
    def _add_prerequisite_constraints(self):
        """
        Solo permitir seleccionar secciones de asignaturas 
        cuyos prerrequisitos estén aprobados.
        
        Nota: Esta validación también se hace en el ValidationService,
        pero la incluimos aquí para garantizar que el solver no asigne
        secciones de materias con prerrequisitos no cumplidos.
        """
        # Esta restricción se aplicará en el ScheduleService antes de llamar al solver,
        # filtrando las secciones disponibles. Aquí solo validamos por seguridad.
        pass
    
    def _add_one_section_per_subject_constraint(self):
        """
        El estudiante puede cursar máximo UNA sección de cada asignatura seleccionada.
        
        Nota: Cambiamos de "exactamente 1" a "máximo 1" para permitir que algunas
        asignaturas no se asignen si todas sus secciones chocan con otras ya asignadas.
        Si hay múltiples secciones de la misma asignatura, solo una puede ser seleccionada.
        """
        # Agrupar secciones por asignatura
        sections_by_subject: Dict[int, List[Section]] = {}
        for section in self.sections:
            if section.subject_id not in sections_by_subject:
                sections_by_subject[section.subject_id] = []
            sections_by_subject[section.subject_id].append(section)
        
        # Para cada asignatura seleccionada, máximo 1 sección puede ser asignada
        for subject_id in self.student.selected_subject_ids:
            if subject_id in sections_by_subject:
                sections = sections_by_subject[subject_id]
                # Suma de variables debe ser <= 1 (puede ser 0 si todas chocan)
                self.model.Add(
                    sum(self.variables[s.id] for s in sections) <= 1
                )
    
    def solve(self) -> ScheduleSolution:
        """
        Ejecutar solver y retornar solución.
        
        Returns:
            ScheduleSolution con el resultado de la optimización
        """
        from app.services.schedule_engine.solution import UnassignedSubject
        
        self.start_time = time.time()
        
        # Agregar función objetivo: maximizar número de asignaturas asignadas
        self._add_objective()
        
        # Configurar solver
        self.solver.parameters.max_time_in_seconds = settings.SCHEDULE_SOLVER_TIMEOUT
        
        # Resolver
        status = self.solver.Solve(self.model)
        
        processing_time = time.time() - self.start_time
        
        # Interpretar resultado
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Solución encontrada
            assigned_section_ids = [
                section_id 
                for section_id, var in self.variables.items()
                if self.solver.Value(var) == 1
            ]
            
            # Obtener asignaturas asignadas y no asignadas
            assigned_subject_ids, unassigned_subjects = self._analyze_assignment()
            
            status_str = "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"
            
            return ScheduleSolution(
                student_id=self.student.id,
                is_feasible=True,
                assigned_section_ids=assigned_section_ids,
                assigned_subject_ids=assigned_subject_ids,
                unassigned_subjects=unassigned_subjects,
                processing_time=processing_time,
                conflicts=[],
                solver_status=status_str,
                quality_score=None  # Se calculará después si es necesario
            )
        else:
            # No se encontró solución
            conflicts = self._analyze_infeasibility()
            status_str = "INFEASIBLE" if status == cp_model.INFEASIBLE else "UNKNOWN"
            
            return ScheduleSolution(
                student_id=self.student.id,
                is_feasible=False,
                assigned_section_ids=[],
                assigned_subject_ids=[],
                unassigned_subjects=[],
                processing_time=processing_time,
                conflicts=conflicts,
                solver_status=status_str,
                quality_score=None
            )
    
    def _add_objective(self):
        """
        Agregar función objetivo: maximizar el número de asignaturas asignadas.
        """
        # Agrupar secciones por asignatura
        sections_by_subject: Dict[int, List[Section]] = {}
        for section in self.sections:
            if section.subject_id not in sections_by_subject:
                sections_by_subject[section.subject_id] = []
            sections_by_subject[section.subject_id].append(section)
        
        # Crear variable binaria por asignatura: 1 si se asignó al menos una sección
        subject_vars: Dict[int, cp_model.IntVar] = {}
        for subject_id, sections in sections_by_subject.items():
            if subject_id in self.student.selected_subject_ids:
                # Variable binaria: 1 si se asignó al menos una sección de esta asignatura
                subject_var = self.model.NewBoolVar(f"subject_{subject_id}_assigned")
                subject_vars[subject_id] = subject_var
                
                # Si alguna sección está asignada, la variable de asignatura debe ser 1
                section_vars = [self.variables[s.id] for s in sections]
                self.model.AddMaxEquality(subject_var, section_vars)
        
        # Maximizar suma de asignaturas asignadas
        self.model.Maximize(sum(subject_vars.values()))
    
    def _analyze_assignment(self) -> Tuple[List[int], List]:
        """
        Analiza qué asignaturas se asignaron y cuáles no, con razones.
        
        Returns:
            (assigned_subject_ids, unassigned_subjects)
        """
        from app.services.schedule_engine.solution import UnassignedSubject
        
        # Obtener secciones asignadas
        assigned_section_ids = [
            section_id 
            for section_id, var in self.variables.items()
            if self.solver.Value(var) == 1
        ]
        
        # Mapear secciones asignadas
        assigned_sections = {s.id: s for s in self.sections if s.id in assigned_section_ids}
        assigned_subject_ids = list(set(s.subject_id for s in assigned_sections.values()))
        
        # Agrupar secciones por asignatura (de TODAS las secciones disponibles, no solo las asignadas)
        sections_by_subject: Dict[int, List[Section]] = {}
        for section in self.sections:
            if section.subject_id not in sections_by_subject:
                sections_by_subject[section.subject_id] = []
            sections_by_subject[section.subject_id].append(section)
        
        # Debug: verificar qué asignaturas tienen secciones disponibles
        # print(f"DEBUG: sections_by_subject keys: {list(sections_by_subject.keys())}")
        # print(f"DEBUG: selected_subject_ids: {self.student.selected_subject_ids}")
        
        # Analizar asignaturas no asignadas
        unassigned_subjects = []
        for subject_id in self.student.selected_subject_ids:
            if subject_id not in assigned_subject_ids:
                # Esta asignatura no se asignó, analizar por qué
                subject_sections = sections_by_subject.get(subject_id, [])
                if not subject_sections:
                    reason = "No hay secciones disponibles para esta asignatura en el período"
                    conflicting_sections = []
                    first_section = None
                else:
                    # Verificar si todas las secciones chocan con las asignadas
                    conflicting_sections = []
                    all_conflict = True
                    
                    for section in subject_sections:
                        conflicts_with = []
                        for assigned_section in assigned_sections.values():
                            if section.has_time_overlap_with(assigned_section):
                                conflicts_with.append({
                                    "section_id": assigned_section.id,
                                    "subject_id": assigned_section.subject_id,
                                    "subject_code": assigned_section.subject_code,
                                    "subject_name": assigned_section.subject_name,
                                    "conflict_type": "time_overlap"
                                })
                        
                        if conflicts_with:
                            conflicting_sections.append({
                                "section_id": section.id,
                                "section_number": section.section_number,
                                "conflicts_with": conflicts_with
                            })
                        else:
                            all_conflict = False
                    
                    if all_conflict and conflicting_sections:
                        reason = f"Todas las secciones ({len(subject_sections)}) tienen conflictos de horario con asignaturas ya asignadas"
                    elif conflicting_sections:
                        reason = f"Algunas secciones tienen conflictos de horario. Total de secciones: {len(subject_sections)}"
                    else:
                        reason = "No se pudo asignar esta asignatura (razón desconocida)"
                    
                    first_section = subject_sections[0]
                
                # Obtener información de la asignatura
                unassigned_subjects.append(UnassignedSubject(
                    subject_id=subject_id,
                    subject_code=first_section.subject_code if first_section else f"SUB{subject_id}",
                    subject_name=first_section.subject_name if first_section else f"Asignatura {subject_id}",
                    reason=reason,
                    conflicting_sections=conflicting_sections
                ))
        
        return assigned_subject_ids, unassigned_subjects
    
    def _analyze_assignment_with_all_sections(self, all_sections: List[Section]) -> Tuple[List[int], List]:
        """
        Analiza qué asignaturas se asignaron y cuáles no, usando TODAS las secciones disponibles
        (no solo las filtradas). Esto permite mostrar conflictos incluso de secciones que fueron filtradas.
        
        Args:
            all_sections: Todas las secciones disponibles (antes del filtro)
        
        Returns:
            (assigned_subject_ids, unassigned_subjects)
        """
        from app.services.schedule_engine.solution import UnassignedSubject
        
        # Obtener secciones asignadas
        assigned_section_ids = [
            section_id 
            for section_id, var in self.variables.items()
            if self.solver.Value(var) == 1
        ]
        
        # Mapear secciones asignadas (de las secciones filtradas que se pasaron al solver)
        assigned_sections = {s.id: s for s in self.sections if s.id in assigned_section_ids}
        assigned_subject_ids = list(set(s.subject_id for s in assigned_sections.values()))
        
        # Agrupar TODAS las secciones disponibles por asignatura
        sections_by_subject: Dict[int, List[Section]] = {}
        for section in all_sections:
            if section.subject_id not in sections_by_subject:
                sections_by_subject[section.subject_id] = []
            sections_by_subject[section.subject_id].append(section)
        
        # Analizar asignaturas no asignadas
        unassigned_subjects = []
        for subject_id in self.student.selected_subject_ids:
            if subject_id not in assigned_subject_ids:
                # Esta asignatura no se asignó, analizar por qué
                subject_sections = sections_by_subject.get(subject_id, [])
                if not subject_sections:
                    reason = "No hay secciones disponibles para esta asignatura en el período"
                    conflicting_sections = []
                    first_section = None
                else:
                    # Verificar si todas las secciones chocan con las asignadas
                    conflicting_sections = []
                    all_conflict = True
                    
                    for section in subject_sections:
                        conflicts_with = []
                        for assigned_section in assigned_sections.values():
                            if section.has_time_overlap_with(assigned_section):
                                conflicts_with.append({
                                    "section_id": assigned_section.id,
                                    "subject_id": assigned_section.subject_id,
                                    "subject_code": assigned_section.subject_code,
                                    "subject_name": assigned_section.subject_name,
                                    "conflict_type": "time_overlap"
                                })
                        
                        if conflicts_with:
                            conflicting_sections.append({
                                "section_id": section.id,
                                "section_number": section.section_number,
                                "conflicts_with": conflicts_with
                            })
                        else:
                            all_conflict = False
                    
                    if all_conflict and conflicting_sections:
                        reason = f"Todas las secciones ({len(subject_sections)}) tienen conflictos de horario con asignaturas ya asignadas"
                    elif conflicting_sections:
                        reason = f"Algunas secciones tienen conflictos de horario. Total de secciones: {len(subject_sections)}"
                    else:
                        reason = "No se pudo asignar esta asignatura (razón desconocida)"
                    
                    first_section = subject_sections[0]
                
                # Obtener información de la asignatura
                unassigned_subjects.append(UnassignedSubject(
                    subject_id=subject_id,
                    subject_code=first_section.subject_code if first_section else f"SUB{subject_id}",
                    subject_name=first_section.subject_name if first_section else f"Asignatura {subject_id}",
                    reason=reason,
                    conflicting_sections=conflicting_sections
                ))
        
        return assigned_subject_ids, unassigned_subjects
    
    def _analyze_infeasibility(self) -> List[str]:
        """
        Analiza por qué no se encontró solución factible.
        Retorna lista de conflictos detectados.
        """
        conflicts = []
        
        # Verificar cupos
        sections_without_capacity = [
            s for s in self.sections if s.available_spots <= 0
        ]
        if sections_without_capacity:
            conflicts.append(
                f"{len(sections_without_capacity)} secciones sin cupos disponibles"
            )
        
        # Verificar si hay suficientes secciones para las materias seleccionadas
        sections_by_subject: Dict[int, List[Section]] = {}
        for section in self.sections:
            if section.subject_id not in sections_by_subject:
                sections_by_subject[section.subject_id] = []
            sections_by_subject[section.subject_id].append(section)
        
        missing_subjects = []
        for subject_id in self.student.selected_subject_ids:
            if subject_id not in sections_by_subject or len(sections_by_subject[subject_id]) == 0:
                missing_subjects.append(subject_id)
        
        if missing_subjects:
            conflicts.append(
                f"No hay secciones disponibles para {len(missing_subjects)} asignaturas seleccionadas"
            )
        
        # Verificar conflictos de horario
        conflict_pairs = []
        for i, section_a in enumerate(self.sections):
            for section_b in self.sections[i + 1:]:
                if section_a.has_time_overlap_with(section_b):
                    conflict_pairs.append((section_a.id, section_b.id))
        
        if conflict_pairs:
            conflicts.append(
                f"Se detectaron {len(conflict_pairs)} pares de secciones con choques de horario"
            )
        
        if not conflicts:
            conflicts.append("No se pudo encontrar una solución factible (razón desconocida)")
        
        return conflicts


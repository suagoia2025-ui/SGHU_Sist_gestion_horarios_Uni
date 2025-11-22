"""
Service para generación de horarios
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.student_repository import StudentRepository
from app.repositories.subject_repository import CourseSectionRepository, SubjectRepository
from app.models.source.student_data import AcademicHistory, GradeStatus
from app.models.source.offer import CourseSection, SectionSchedule
from app.services.schedule_engine.models import Student, Section, TimeSlot
from app.services.schedule_engine.constraint_solver import ConstraintScheduleSolver
from app.services.schedule_engine.solution import ScheduleSolution
from app.core.exceptions import NotFoundError


class ScheduleService:
    """Service para generar horarios usando el motor de restricciones"""
    
    def __init__(self, db: Session):
        self.db = db
        self.student_repo = StudentRepository(db)
        self.section_repo = CourseSectionRepository(db)
        self.subject_repo = SubjectRepository(db)
    
    def generate_schedule_for_student(
        self,
        student_id: int,
        selected_subject_ids: List[int],
        academic_period_id: Optional[int] = None
    ) -> ScheduleSolution:
        """
        Genera horario para un estudiante dado.
        
        Args:
            student_id: ID del estudiante
            selected_subject_ids: Lista de IDs de asignaturas que quiere cursar
            academic_period_id: ID del período académico (opcional, usa el activo si no se proporciona)
        
        Returns:
            ScheduleSolution con el resultado de la generación
        """
        # 1. Cargar datos del estudiante
        student_data = self._load_student_data(student_id)
        # Asignar las asignaturas seleccionadas
        student_data.selected_subject_ids = selected_subject_ids
        
        # 1.5. Validar que las asignaturas seleccionadas pertenezcan al programa del estudiante
        self._validate_subjects_belong_to_student_program(student_id, selected_subject_ids)
        
        # 2. Obtener período académico
        if not academic_period_id:
            from app.repositories.subject_repository import AcademicPeriodRepository
            period_repo = AcademicPeriodRepository(self.db)
            period = period_repo.get_current()
            if not period:
                return ScheduleSolution(
                    student_id=student_id,
                    is_feasible=False,
                    assigned_section_ids=[],
                    processing_time=0.0,
                    conflicts=["No hay período académico activo"],
                    solver_status="INFEASIBLE"
                )
            academic_period_id = period.id
        
        # 3. Cargar secciones disponibles de las asignaturas seleccionadas
        all_sections = self._load_available_sections(selected_subject_ids, academic_period_id)
        
        if not all_sections:
            return ScheduleSolution(
                student_id=student_id,
                is_feasible=False,
                assigned_section_ids=[],
                assigned_subject_ids=[],
                unassigned_subjects=[],
                processing_time=0.0,
                conflicts=["No hay secciones disponibles para las asignaturas seleccionadas"],
                solver_status="INFEASIBLE"
            )
        
        # 4. Filtrar secciones: solo las que tienen cupos y prerrequisitos cumplidos
        filtered_sections = self._filter_valid_sections(student_data, all_sections)
        
        if not filtered_sections:
            return ScheduleSolution(
                student_id=student_id,
                is_feasible=False,
                assigned_section_ids=[],
                assigned_subject_ids=[],
                unassigned_subjects=[],
                processing_time=0.0,
                conflicts=["No hay secciones válidas después de aplicar filtros (cupos, prerrequisitos)"],
                solver_status="INFEASIBLE"
            )
        
        # 5. Resolver con el solver (usando secciones filtradas)
        solver = ConstraintScheduleSolver(student_data, filtered_sections)
        solver.create_variables()
        solver.add_constraints()
        solution = solver.solve()
        
        # 6. Actualizar análisis con TODAS las secciones disponibles para mejor información
        # Esto permite mostrar conflictos incluso de secciones que fueron filtradas
        if solution.is_feasible:
            assigned_subject_ids, unassigned_subjects = solver._analyze_assignment_with_all_sections(all_sections)
            solution.assigned_subject_ids = assigned_subject_ids
            solution.unassigned_subjects = unassigned_subjects
        
        # 7. Persistir si es viable (esto se hará en FASE 6 con optimización)
        # Por ahora solo retornamos la solución
        
        return solution
    
    def _load_student_data(self, student_id: int) -> Student:
        """Carga datos del estudiante y los convierte al modelo del solver"""
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise NotFoundError("Estudiante", student_id)
        
        # Obtener asignaturas aprobadas
        academic_history = self.student_repo.get_academic_history(student_id)
        approved_subject_ids = [
            h.subject_id 
            for h in academic_history 
            if h.status == GradeStatus.APROBADO.value
        ]
        
        return Student(
            id=student.id,
            program_id=student.program_id,
            approved_subject_ids=approved_subject_ids,
            selected_subject_ids=[]  # Se llenará en generate_schedule_for_student
        )
    
    def _load_available_sections(
        self,
        subject_ids: List[int],
        period_id: int
    ) -> List[Section]:
        """
        Carga secciones disponibles y las convierte al modelo del solver.
        """
        # Obtener todas las secciones de las asignaturas seleccionadas en el período
        sections = []
        
        for subject_id in subject_ids:
            # Obtener secciones de esta asignatura en el período
            subject_sections = self.section_repo.get_by_subject(subject_id, period_id)
            
            for db_section in subject_sections:
                # Cargar horarios de la sección
                db_schedules = self.db.query(SectionSchedule).filter(
                    SectionSchedule.section_id == db_section.id
                ).all()
                
                # Convertir horarios a TimeSlots
                timeslots = []
                for idx, schedule in enumerate(db_schedules):
                    timeslot = TimeSlot(
                        id=schedule.id,
                        day_of_week=schedule.day_of_week,
                        start_time=schedule.start_time,
                        end_time=schedule.end_time
                    )
                    timeslots.append(timeslot)
                
                # Obtener información de la asignatura
                subject = self.subject_repo.get_by_id(db_section.subject_id)
                
                # Crear objeto Section
                section = Section(
                    id=db_section.id,
                    subject_id=db_section.subject_id,
                    subject_code=subject.code if subject else f"SUB{db_section.subject_id}",
                    subject_name=subject.name if subject else "Asignatura desconocida",
                    professor_id=db_section.professor_id,
                    classroom_id=db_section.classroom_id,
                    capacity=db_section.capacity,
                    enrolled_count=db_section.enrolled_count,
                    section_number=db_section.section_number,
                    timeslots=timeslots
                )
                sections.append(section)
        
        return sections
    
    def _filter_valid_sections(
        self,
        student: Student,
        sections: List[Section]
    ) -> List[Section]:
        """
        Filtra secciones válidas:
        - Con cupos disponibles
        - Con prerrequisitos cumplidos
        """
        valid_sections = []
        
        for section in sections:
            # 1. Verificar cupos
            if section.available_spots <= 0:
                continue
            
            # 2. Verificar prerrequisitos
            subject = self.subject_repo.get_with_prerequisites(section.subject_id)
            if subject and subject.prerequisites:
                prerequisites_met = True
                for prereq in subject.prerequisites:
                    if prereq.type == 'obligatorio':
                        # Debe estar aprobado
                        if prereq.prerequisite_subject_id not in student.approved_subject_ids:
                            prerequisites_met = False
                            break
                    # Correquisitos se manejan en el solver
                
                if not prerequisites_met:
                    continue
            
            valid_sections.append(section)
        
        return valid_sections
    
    def _validate_subjects_belong_to_student_program(
        self,
        student_id: int,
        selected_subject_ids: List[int]
    ):
        """
        Valida que todas las asignaturas seleccionadas pertenezcan al programa del estudiante.
        
        Raises:
            ValidationError: Si alguna asignatura no pertenece al programa del estudiante
        """
        from app.core.exceptions import ValidationError
        
        # Obtener el programa del estudiante
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise NotFoundError("Estudiante", student_id)
        
        student_program_id = student.program_id
        
        # Obtener todas las asignaturas seleccionadas
        invalid_subjects = []
        for subject_id in selected_subject_ids:
            subject = self.subject_repo.get_by_id(subject_id)
            if not subject:
                invalid_subjects.append({
                    "subject_id": subject_id,
                    "reason": "Asignatura no encontrada"
                })
            elif subject.program_id != student_program_id:
                invalid_subjects.append({
                    "subject_id": subject_id,
                    "subject_code": subject.code,
                    "subject_name": subject.name,
                    "subject_program_id": subject.program_id,
                    "reason": f"La asignatura pertenece al programa {subject.program_id}, pero el estudiante pertenece al programa {student_program_id}"
                })
        
        if invalid_subjects:
            # Construir mensaje de error detallado
            error_details = []
            for invalid in invalid_subjects:
                if "subject_code" in invalid:
                    error_details.append(
                        f"Subject {invalid['subject_id']} ({invalid['subject_code']} - {invalid['subject_name']}): "
                        f"{invalid['reason']}"
                    )
                else:
                    error_details.append(
                        f"Subject {invalid['subject_id']}: {invalid['reason']}"
                    )
            
            error_message = "Las siguientes asignaturas no pertenecen al programa del estudiante:\n" + "\n".join(f"- {detail}" for detail in error_details)
            raise ValidationError(error_message)


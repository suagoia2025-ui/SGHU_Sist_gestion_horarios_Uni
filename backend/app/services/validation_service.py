"""
Service para validaciones de reglas de negocio
"""
from typing import List, Optional, Dict, Any
from datetime import time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.repositories.student_repository import StudentRepository
from app.repositories.subject_repository import (
    SubjectRepository,
    CourseSectionRepository,
    AcademicPeriodRepository
)
from app.models.source.student_data import AcademicHistory, FinancialStatus, GradeStatus
from app.models.source.academic import Prerequisite, Subject
from app.models.source.rules import AcademicRule
from app.models.source.offer import CourseSection, SectionSchedule
from app.schemas.validation import ValidationResult


class ValidationService:
    """Service para validar reglas de negocio de matrícula"""
    
    def __init__(self, db: Session):
        self.db = db
        self.student_repo = StudentRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.section_repo = CourseSectionRepository(db)
        self.period_repo = AcademicPeriodRepository(db)
    
    def validate_financial_status(self, student_id: int) -> ValidationResult:
        """
        Verifica estado financiero del estudiante.
        Bloquea matrícula si tiene deudas.
        """
        financial_status = self.student_repo.get_financial_status(student_id)
        
        if not financial_status:
            return ValidationResult(
                validation_type="financial_status",
                is_valid=False,
                message="No se encontró información financiera del estudiante",
                details={"student_id": student_id}
            )
        
        if financial_status.has_debt == 'true':
            return ValidationResult(
                validation_type="financial_status",
                is_valid=False,
                message=f"Tienes una deuda pendiente de ${financial_status.debt_amount:.2f}",
                details={
                    "student_id": student_id,
                    "has_debt": True,
                    "debt_amount": float(financial_status.debt_amount),
                    "payment_status": financial_status.payment_status
                }
            )
        
        return ValidationResult(
            validation_type="financial_status",
            is_valid=True,
            message="Estado financiero válido",
            details={
                "student_id": student_id,
                "has_debt": False,
                "payment_status": financial_status.payment_status
            }
        )
    
    def validate_prerequisites(
        self,
        student_id: int,
        subject_id: int,
        selected_subject_ids: Optional[List[int]] = None
    ) -> ValidationResult:
        """
        Verifica si el estudiante cumple prerrequisitos de una asignatura.
        Considera correquisitos si están en la selección actual.
        """
        # Obtener prerrequisitos de la asignatura
        prerequisites = self.db.query(Prerequisite).filter(
            Prerequisite.subject_id == subject_id
        ).all()
        
        if not prerequisites:
            return ValidationResult(
                validation_type="prerequisites",
                is_valid=True,
                message="La asignatura no tiene prerrequisitos",
                details={"subject_id": subject_id}
            )
        
        # Obtener historial académico del estudiante
        academic_history = self.student_repo.get_academic_history(student_id)
        approved_subject_ids = {
            h.subject_id for h in academic_history
            if h.status == GradeStatus.APROBADO.value
        }
        
        # Incluir correquisitos si están en la selección actual
        if selected_subject_ids:
            approved_subject_ids.update(selected_subject_ids)
        
        missing_prerequisites = []
        missing_prerequisite_names = []
        
        for prereq in prerequisites:
            prereq_subject = self.subject_repo.get_by_id(prereq.prerequisite_subject_id)
            prereq_name = prereq_subject.name if prereq_subject else f"ID {prereq.prerequisite_subject_id}"
            
            if prereq.type == 'correquisito':
                # Correquisito: puede estar en la selección actual
                if prereq.prerequisite_subject_id not in approved_subject_ids:
                    missing_prerequisites.append(prereq.prerequisite_subject_id)
                    missing_prerequisite_names.append(prereq_name)
            else:  # obligatorio
                # Prerrequisito obligatorio: debe estar aprobado
                if prereq.prerequisite_subject_id not in approved_subject_ids:
                    missing_prerequisites.append(prereq.prerequisite_subject_id)
                    missing_prerequisite_names.append(prereq_name)
        
        if missing_prerequisites:
            return ValidationResult(
                validation_type="prerequisites",
                is_valid=False,
                message=f"Debes aprobar las siguientes materias primero: {', '.join(missing_prerequisite_names)}",
                details={
                    "subject_id": subject_id,
                    "missing_prerequisites": missing_prerequisites,
                    "missing_prerequisite_names": missing_prerequisite_names
                }
            )
        
        return ValidationResult(
            validation_type="prerequisites",
            is_valid=True,
            message="Prerrequisitos cumplidos",
            details={"subject_id": subject_id}
        )
    
    def validate_credit_limit(
        self,
        student_id: int,
        selected_subject_ids: List[int]
    ) -> ValidationResult:
        """
        Verifica límite de créditos.
        Obtiene reglas académicas y verifica máximo y mínimo.
        """
        # Obtener reglas académicas
        max_credits_rule = self.db.query(AcademicRule).filter(
            AcademicRule.rule_type == 'max_credits'
        ).first()
        
        min_credits_rule = self.db.query(AcademicRule).filter(
            AcademicRule.rule_type == 'min_credits'
        ).first()
        
        max_credits = int(max_credits_rule.rule_value) if max_credits_rule else 20
        min_credits = int(min_credits_rule.rule_value) if min_credits_rule else 8
        
        # Validar que haya asignaturas seleccionadas
        if not selected_subject_ids:
            return ValidationResult(
                validation_type="credit_limit",
                is_valid=False,
                message="No se seleccionaron asignaturas",
                details={
                    "total_credits": 0,
                    "max_allowed": max_credits,
                    "min_required": min_credits
                }
            )
        
        # Calcular créditos totales de las asignaturas seleccionadas
        subjects = self.db.query(Subject).filter(
            Subject.id.in_(selected_subject_ids)
        ).all()
        
        # Verificar que todas las asignaturas existen
        found_subject_ids = {s.id for s in subjects}
        missing_subject_ids = set(selected_subject_ids) - found_subject_ids
        
        if missing_subject_ids:
            return ValidationResult(
                validation_type="credit_limit",
                is_valid=False,
                message=f"Algunas asignaturas no existen: {list(missing_subject_ids)}",
                details={
                    "missing_subject_ids": list(missing_subject_ids),
                    "selected_subject_ids": selected_subject_ids
                }
            )
        
        total_credits = sum(subject.credits for subject in subjects)
        
        if total_credits > max_credits:
            return ValidationResult(
                validation_type="credit_limit",
                is_valid=False,
                message=f"Excedes el límite máximo de créditos. Máximo permitido: {max_credits} créditos. Seleccionaste: {total_credits} créditos",
                details={
                    "total_credits": total_credits,
                    "max_allowed": max_credits,
                    "min_required": min_credits,
                    "excess": total_credits - max_credits
                }
            )
        
        if total_credits < min_credits:
            return ValidationResult(
                validation_type="credit_limit",
                is_valid=False,
                message=f"No cumples el mínimo de créditos. Mínimo requerido: {min_credits} créditos. Seleccionaste: {total_credits} créditos",
                details={
                    "total_credits": total_credits,
                    "max_allowed": max_credits,
                    "min_required": min_credits,
                    "deficit": min_credits - total_credits
                }
            )
        
        return ValidationResult(
            validation_type="credit_limit",
            is_valid=True,
            message=f"Límite de créditos válido ({total_credits} créditos)",
            details={
                "total_credits": total_credits,
                "max_allowed": max_credits,
                "min_required": min_credits
            }
        )
    
    def validate_section_capacity(self, section_id: int) -> ValidationResult:
        """
        Verifica cupos disponibles en una sección.
        """
        section = self.section_repo.get_by_id(section_id)
        
        if not section:
            return ValidationResult(
                validation_type="section_capacity",
                is_valid=False,
                message=f"Sección {section_id} no encontrada",
                details={"section_id": section_id}
            )
        
        available = section.capacity - section.enrolled_count
        
        if available <= 0:
            return ValidationResult(
                validation_type="section_capacity",
                is_valid=False,
                message=f"No hay cupos disponibles en la sección {section.section_number}",
                details={
                    "section_id": section_id,
                    "capacity": section.capacity,
                    "enrolled_count": section.enrolled_count,
                    "available": available
                }
            )
        
        return ValidationResult(
            validation_type="section_capacity",
            is_valid=True,
            message=f"Cupos disponibles: {available} de {section.capacity}",
            details={
                "section_id": section_id,
                "capacity": section.capacity,
                "enrolled_count": section.enrolled_count,
                "available": available
            }
        )
    
    def validate_schedule_conflicts(self, section_ids: List[int]) -> ValidationResult:
        """
        Detecta choques de horario entre secciones.
        """
        if len(section_ids) < 2:
            return ValidationResult(
                validation_type="schedule_conflicts",
                is_valid=True,
                message="No hay suficientes secciones para detectar conflictos",
                details={"section_ids": section_ids}
            )
        
        # Obtener horarios de todas las secciones
        schedules = self.db.query(SectionSchedule).filter(
            SectionSchedule.section_id.in_(section_ids)
        ).all()
        
        # Agrupar por sección
        schedules_by_section: Dict[int, List[SectionSchedule]] = {}
        for schedule in schedules:
            if schedule.section_id not in schedules_by_section:
                schedules_by_section[schedule.section_id] = []
            schedules_by_section[schedule.section_id].append(schedule)
        
        # Detectar conflictos
        conflicts = []
        section_ids_list = list(schedules_by_section.keys())
        
        for i in range(len(section_ids_list)):
            for j in range(i + 1, len(section_ids_list)):
                section_a_id = section_ids_list[i]
                section_b_id = section_ids_list[j]
                
                schedules_a = schedules_by_section[section_a_id]
                schedules_b = schedules_by_section[section_b_id]
                
                # Verificar si hay solapamiento entre cualquier par de horarios
                for sched_a in schedules_a:
                    for sched_b in schedules_b:
                        if self._schedules_overlap(sched_a, sched_b):
                            # Obtener información de las secciones
                            section_a = self.section_repo.get_by_id(section_a_id)
                            section_b = self.section_repo.get_by_id(section_b_id)
                            
                            conflict_info = {
                                "section_a_id": section_a_id,
                                "section_b_id": section_b_id,
                                "day": sched_a.day_of_week,
                                "time_a": f"{sched_a.start_time}-{sched_a.end_time}",
                                "time_b": f"{sched_b.start_time}-{sched_b.end_time}",
                                "section_a_name": f"Sección {section_a_id}",
                                "section_b_name": f"Sección {section_b_id}"
                            }
                            
                            # Agregar nombres si las secciones existen
                            if section_a:
                                subject_a_name = section_a.subject.name if section_a.subject else f"ID {section_a.subject_id}"
                                conflict_info["section_a_name"] = f"{subject_a_name} - Sección {section_a.section_number}"
                            
                            if section_b:
                                subject_b_name = section_b.subject.name if section_b.subject else f"ID {section_b.subject_id}"
                                conflict_info["section_b_name"] = f"{subject_b_name} - Sección {section_b.section_number}"
                            
                            conflicts.append(conflict_info)
        
        if conflicts:
            conflict_messages = [
                f"{c.get('section_a_name', f'Sección {c["section_a_id"]}')} y "
                f"{c.get('section_b_name', f'Sección {c["section_b_id"]}')} "
                f"(Día {c['day']}, {c['time_a']} vs {c['time_b']})"
                for c in conflicts
            ]
            
            return ValidationResult(
                validation_type="schedule_conflicts",
                is_valid=False,
                message=f"Conflicto de horario detectado: {'; '.join(conflict_messages)}",
                details={
                    "conflicts": conflicts,
                    "conflict_count": len(conflicts)
                }
            )
        
        return ValidationResult(
            validation_type="schedule_conflicts",
            is_valid=True,
            message="No hay conflictos de horario",
            details={"section_ids": section_ids}
        )
    
    def _schedules_overlap(self, schedule_a: SectionSchedule, schedule_b: SectionSchedule) -> bool:
        """Verifica si dos horarios se solapan"""
        # Deben ser el mismo día
        if schedule_a.day_of_week != schedule_b.day_of_week:
            return False
        
        # Verificar solapamiento de tiempo
        return not (schedule_a.end_time <= schedule_b.start_time or schedule_b.end_time <= schedule_a.start_time)
    
    def validate_duplicate_enrollment(
        self,
        student_id: int,
        subject_id: int
    ) -> ValidationResult:
        """
        Verifica si ya está matriculado o ya aprobó la materia.
        Permite repetir solo si fue reprobada.
        """
        # Verificar en historial académico
        academic_history = self.db.query(AcademicHistory).filter(
            and_(
                AcademicHistory.student_id == student_id,
                AcademicHistory.subject_id == subject_id
            )
        ).first()
        
        if academic_history:
            if academic_history.status == GradeStatus.APROBADO.value:
                return ValidationResult(
                    validation_type="duplicate_enrollment",
                    is_valid=False,
                    message=f"Ya aprobaste esta asignatura con calificación {academic_history.grade}",
                    details={
                        "student_id": student_id,
                        "subject_id": subject_id,
                        "status": "ya_aprobado",
                        "grade": float(academic_history.grade) if academic_history.grade else None,
                        "period": academic_history.period
                    }
                )
            elif academic_history.status == GradeStatus.REPROBADO.value:
                return ValidationResult(
                    validation_type="duplicate_enrollment",
                    is_valid=True,
                    message="Puedes repetir esta asignatura (fue reprobada anteriormente)",
                    details={
                        "student_id": student_id,
                        "subject_id": subject_id,
                        "status": "repeticion",
                        "previous_grade": float(academic_history.grade) if academic_history.grade else None,
                        "previous_period": academic_history.period
                    }
                )
        
        # Verificar si está actualmente matriculado (en el esquema sghu)
        # Esto se implementará cuando tengamos las tablas de matrícula pobladas
        # Por ahora, solo verificamos el historial académico
        
        return ValidationResult(
            validation_type="duplicate_enrollment",
            is_valid=True,
            message="Matrícula nueva permitida",
            details={
                "student_id": student_id,
                "subject_id": subject_id,
                "status": "nuevo"
            }
        )


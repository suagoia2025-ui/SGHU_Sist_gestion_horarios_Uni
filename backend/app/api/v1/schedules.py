"""
Endpoints para generación de horarios
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.schedule_service import ScheduleService
from app.schemas.schedule import (
    ScheduleGenerationRequest,
    ScheduleSolutionResponse,
    UnassignedSubjectInfo,
    GeneratedScheduleRead,
    ScheduleListResponse,
    ScheduleComparisonResponse,
    ScheduleStatsResponse,
    ScheduleSlotDetailRead
)
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter()


@router.post("/generate", response_model=ScheduleSolutionResponse)
def generate_schedule(
    request: ScheduleGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Genera horario para estudiante usando motor híbrido (OR-Tools + Algoritmo Genético).
    
    El sistema intenta asignar secciones de las asignaturas seleccionadas
    respetando restricciones duras y optimizando restricciones blandas.
    
    Restricciones duras (obligatorias):
    - Sin choques de horario
    - Cupos disponibles
    - Sin conflictos de profesor/aula
    - Una sección por asignatura
    - Prerrequisitos cumplidos
    
    Restricciones blandas (optimización):
    - Minimizar gaps entre clases
    - Distribución balanceada en la semana
    - Preferencia de horarios (8am-6pm)
    - Días libres
    
    Body:
    {
        "student_id": 1,
        "selected_subject_ids": [1, 2, 3, 4, 5],
        "academic_period_id": 1,  // Opcional, usa el activo si no se proporciona
        "optimization_level": "medium"  // "none" | "low" | "medium" | "high"
    }
    """
    try:
        service = ScheduleService(db)
        solution = service.generate_schedule_for_student(
            student_id=request.student_id,
            selected_subject_ids=request.selected_subject_ids,
            academic_period_id=request.academic_period_id,
            optimization_level=request.optimization_level or "none"
        )
        
        return ScheduleSolutionResponse(
            student_id=solution.student_id,
            is_feasible=solution.is_feasible,
            assigned_section_ids=solution.assigned_section_ids,
            assigned_subject_ids=solution.assigned_subject_ids,
            unassigned_subjects=[
                UnassignedSubjectInfo(
                    subject_id=u.subject_id,
                    subject_code=u.subject_code,
                    subject_name=u.subject_name,
                    reason=u.reason,
                    conflicting_sections=u.conflicting_sections
                )
                for u in solution.unassigned_subjects
            ],
            processing_time=solution.processing_time,
            conflicts=solution.conflicts,
            solver_status=solution.solver_status,
            quality_score=solution.quality_score
        )
    except NotFoundError as e:
        raise e
    except ValidationError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando horario: {str(e)}"
        )


@router.get("/students/{student_id}", response_model=ScheduleListResponse)
def get_student_schedules(
    student_id: int,
    limit: int = Query(10, ge=1, le=100, description="Número máximo de horarios a retornar"),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los horarios generados para un estudiante.
    
    Retorna los horarios más recientes primero, incluyendo:
    - ID del horario
    - Método de generación
    - Quality score
    - Tiempo de procesamiento
    - Estado
    - Fecha de creación
    - Slots de horario (si se solicita)
    """
    service = ScheduleService(db)
    schedules = service.get_generated_schedules_for_student(student_id)
    
    if not schedules:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron horarios para el estudiante {student_id}"
        )
    
    # Limitar resultados
    schedules = schedules[:limit]
    
    # Convertir a schemas con información adicional
    schedule_reads = []
    for schedule in schedules:
        # Obtener información adicional de los slots
        schedule_details = service.get_schedule_details(schedule.id)
        
        slots = []
        if schedule_details and schedule_details.schedule_slots:
            for slot in schedule_details.schedule_slots:
                # Obtener información de la sección
                from app.repositories.subject_repository import CourseSectionRepository
                section_repo = CourseSectionRepository(db)
                section = section_repo.get_by_id(slot.section_id)
                
                slot_detail = ScheduleSlotDetailRead(
                    id=slot.id,
                    schedule_id=slot.schedule_id,
                    section_id=slot.section_id,
                    day_of_week=slot.day_of_week,
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    section_number=section.section_number if section else None,
                    subject_code=section.subject.code if section and section.subject else None,
                    subject_name=section.subject.name if section and section.subject else None,
                    professor_name=f"{section.professor.first_name} {section.professor.last_name}" if section and section.professor else None,
                    classroom_code=section.classroom.code if section and section.classroom else None
                )
                slots.append(slot_detail)
        
        # Obtener student_id del enrollment
        student_id_from_enrollment = schedule.enrollment.student_id if schedule.enrollment else None
        
        schedule_read = GeneratedScheduleRead(
            id=schedule.id,
            enrollment_id=schedule.enrollment_id,
            student_id=student_id_from_enrollment,
            generation_method=schedule.generation_method,
            quality_score=schedule.quality_score,
            processing_time=schedule.processing_time,
            status=schedule.status,
            created_at=schedule.created_at,
            schedule_slots=slots
        )
        schedule_reads.append(schedule_read)
    
    return ScheduleListResponse(
        student_id=student_id,
        total_schedules=len(schedules),
        schedules=schedule_reads
    )


@router.get("/{schedule_id}", response_model=GeneratedScheduleRead)
def get_schedule_details(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles completos de un horario específico.
    
    Incluye:
    - Información del horario (método, quality score, etc.)
    - Todos los slots de horario con detalles de secciones
    - Información de asignaturas, profesores y aulas
    """
    service = ScheduleService(db)
    schedule = service.get_schedule_details(schedule_id)
    
    if not schedule:
        raise HTTPException(
            status_code=404,
            detail=f"Horario con ID {schedule_id} no encontrado"
        )
    
    # Obtener información adicional de los slots
    slots = []
    for slot in schedule.schedule_slots:
        from app.repositories.subject_repository import CourseSectionRepository
        section_repo = CourseSectionRepository(db)
        section = section_repo.get_by_id(slot.section_id)
        
        slot_detail = ScheduleSlotDetailRead(
            id=slot.id,
            schedule_id=slot.schedule_id,
            section_id=slot.section_id,
            day_of_week=slot.day_of_week,
            start_time=slot.start_time,
            end_time=slot.end_time,
            section_number=section.section_number if section else None,
            subject_code=section.subject.code if section and section.subject else None,
            subject_name=section.subject.name if section and section.subject else None,
            professor_name=f"{section.professor.first_name} {section.professor.last_name}" if section and section.professor else None,
            classroom_code=section.classroom.code if section and section.classroom else None
        )
        slots.append(slot_detail)
    
    student_id_from_enrollment = schedule.enrollment.student_id if schedule.enrollment else None
    
    return GeneratedScheduleRead(
        id=schedule.id,
        enrollment_id=schedule.enrollment_id,
        student_id=student_id_from_enrollment,
        generation_method=schedule.generation_method,
        quality_score=schedule.quality_score,
        processing_time=schedule.processing_time,
        status=schedule.status,
        created_at=schedule.created_at,
        schedule_slots=slots
    )


@router.get("/{schedule_id}/compare/{other_schedule_id}", response_model=ScheduleComparisonResponse)
def compare_schedules(
    schedule_id: int,
    other_schedule_id: int,
    db: Session = Depends(get_db)
):
    """
    Compara dos horarios y muestra las diferencias.
    
    Compara:
    - Quality scores
    - Tiempos de procesamiento
    - Métodos de generación
    - Número de asignaturas/secciones
    - Distribución de días
    """
    service = ScheduleService(db)
    
    schedule_1 = service.get_schedule_details(schedule_id)
    schedule_2 = service.get_schedule_details(other_schedule_id)
    
    if not schedule_1:
        raise HTTPException(status_code=404, detail=f"Horario {schedule_id} no encontrado")
    if not schedule_2:
        raise HTTPException(status_code=404, detail=f"Horario {other_schedule_id} no encontrado")
    
    # Convertir a schemas
    def schedule_to_read(schedule):
        slots = []
        for slot in schedule.schedule_slots:
            from app.repositories.subject_repository import CourseSectionRepository
            section_repo = CourseSectionRepository(db)
            section = section_repo.get_by_id(slot.section_id)
            
            slot_detail = ScheduleSlotDetailRead(
                id=slot.id,
                schedule_id=slot.schedule_id,
                section_id=slot.section_id,
                day_of_week=slot.day_of_week,
                start_time=slot.start_time,
                end_time=slot.end_time,
                section_number=section.section_number if section else None,
                subject_code=section.subject.code if section and section.subject else None,
                subject_name=section.subject.name if section and section.subject else None,
                professor_name=f"{section.professor.first_name} {section.professor.last_name}" if section and section.professor else None,
                classroom_code=section.classroom.code if section and section.classroom else None
            )
            slots.append(slot_detail)
        
        student_id_from_enrollment = schedule.enrollment.student_id if schedule.enrollment else None
        
        return GeneratedScheduleRead(
            id=schedule.id,
            enrollment_id=schedule.enrollment_id,
            student_id=student_id_from_enrollment,
            generation_method=schedule.generation_method,
            quality_score=schedule.quality_score,
            processing_time=schedule.processing_time,
            status=schedule.status,
            created_at=schedule.created_at,
            schedule_slots=slots
        )
    
    schedule_1_read = schedule_to_read(schedule_1)
    schedule_2_read = schedule_to_read(schedule_2)
    
    # Calcular comparación
    comparison = {
        "quality_score_diff": None,
        "processing_time_diff": None,
        "sections_count_1": len(set(s.section_id for s in schedule_1.schedule_slots)),
        "sections_count_2": len(set(s.section_id for s in schedule_2.schedule_slots)),
        "slots_count_1": len(schedule_1.schedule_slots),
        "slots_count_2": len(schedule_2.schedule_slots),
        "days_distribution_1": {},
        "days_distribution_2": {},
        "better_quality": None
    }
    
    if schedule_1.quality_score is not None and schedule_2.quality_score is not None:
        comparison["quality_score_diff"] = schedule_1.quality_score - schedule_2.quality_score
        comparison["better_quality"] = schedule_1.id if schedule_1.quality_score < schedule_2.quality_score else schedule_2.id
    
    if schedule_1.processing_time and schedule_2.processing_time:
        comparison["processing_time_diff"] = schedule_1.processing_time - schedule_2.processing_time
    
    # Distribución de días
    for slot in schedule_1.schedule_slots:
        day = slot.day_of_week
        comparison["days_distribution_1"][day] = comparison["days_distribution_1"].get(day, 0) + 1
    
    for slot in schedule_2.schedule_slots:
        day = slot.day_of_week
        comparison["days_distribution_2"][day] = comparison["days_distribution_2"].get(day, 0) + 1
    
    return ScheduleComparisonResponse(
        schedule_1=schedule_1_read,
        schedule_2=schedule_2_read,
        comparison=comparison
    )


@router.get("/students/{student_id}/stats", response_model=ScheduleStatsResponse)
def get_student_schedule_stats(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de todos los horarios generados para un estudiante.
    
    Incluye:
    - Total de horarios
    - Horarios completados vs fallidos
    - Promedio, mejor y peor quality score
    - Tiempo promedio de procesamiento
    - Distribución por método de generación
    """
    service = ScheduleService(db)
    schedules = service.get_generated_schedules_for_student(student_id)
    
    if not schedules:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron horarios para el estudiante {student_id}"
        )
    
    # Calcular estadísticas
    total = len(schedules)
    completed = sum(1 for s in schedules if s.status == 'completed')
    failed = sum(1 for s in schedules if s.status == 'failed')
    
    quality_scores = [s.quality_score for s in schedules if s.quality_score is not None]
    processing_times = [s.processing_time for s in schedules if s.processing_time is not None]
    
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else None
    best_quality = min(quality_scores) if quality_scores else None
    worst_quality = max(quality_scores) if quality_scores else None
    avg_processing = sum(processing_times) / len(processing_times) if processing_times else None
    
    # Distribución por método
    methods = {}
    for schedule in schedules:
        method = schedule.generation_method
        methods[method] = methods.get(method, 0) + 1
    
    return ScheduleStatsResponse(
        student_id=student_id,
        total_schedules=total,
        completed_schedules=completed,
        failed_schedules=failed,
        average_quality_score=avg_quality,
        best_quality_score=best_quality,
        worst_quality_score=worst_quality,
        average_processing_time=avg_processing,
        generation_methods=methods
    )


@router.get("/health")
def schedules_health():
    """
    Health check para módulo de horarios
    """
    return {
        "status": "ok",
        "message": "Módulo de horarios - FASE 6 implementada",
        "features": [
            "Constraint Solver (OR-Tools CP-SAT)",
            "Algoritmo Genético (DEAP)",
            "Motor Híbrido (OR-Tools + AG)",
            "Restricciones duras y blandas",
            "Optimización de calidad de horarios",
            "Persistencia en base de datos",
            "Endpoints de consulta"
        ]
    }

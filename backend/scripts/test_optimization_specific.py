#!/usr/bin/env python3
"""
Pruebas específicas del algoritmo de optimización
Enfocadas en: restricciones blandas, casos extremos, consistencia, componentes del AG
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.schedule_service import ScheduleService
from app.services.subject_service import SubjectService
from app.repositories.student_repository import StudentRepository
from app.repositories.subject_repository import CourseSectionRepository, AcademicPeriodRepository
from app.models.source.offer import SectionSchedule
from app.services.schedule_engine.models import Section, TimeSlot
from app.services.schedule_engine.fitness import ScheduleFitness
from datetime import time, datetime
import json


def print_section(title: str):
    """Imprime un separador de sección"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_gaps_penalty(db: Session):
    """Prueba específica: Validación de penalización por gaps"""
    print_section("PRUEBA ESPECÍFICA: Penalización por Gaps")
    
    service = ScheduleService(db)
    student_repo = StudentRepository(db)
    subject_service = SubjectService(db)
    
    students = student_repo.get_all(limit=1)
    if not students:
        print("❌ No se encontraron estudiantes")
        return
    
    student = students[0]
    subjects = subject_service.get_subjects(program_id=student.program_id, limit=8)
    
    if not subjects:
        print("❌ No hay asignaturas disponibles")
        return
    
    selected_subject_ids = [s.id for s in subjects[:6]]
    
    print(f"\n📚 Objetivo: Validar que la optimización reduce gaps entre clases")
    print(f"   Asignaturas: {len(selected_subject_ids)}")
    
    # Comparar soluciones
    solution_none = service.generate_schedule_for_student(
        student_id=student.id,
        selected_subject_ids=selected_subject_ids,
        optimization_level="none"
    )
    
    solution_high = service.generate_schedule_for_student(
        student_id=student.id,
        selected_subject_ids=selected_subject_ids,
        optimization_level="high"
    )
    
    # Analizar gaps
    def get_gaps_penalty(db, solution):
        if not solution.is_feasible or not solution.assigned_section_ids:
            return None
        
        section_repo = CourseSectionRepository(db)
        sections = []
        
        for section_id in solution.assigned_section_ids:
            db_section = section_repo.get_by_id(section_id)
            if not db_section:
                continue
            
            db_schedules = db.query(SectionSchedule).filter(
                SectionSchedule.section_id == db_section.id
            ).all()
            
            timeslots = []
            for schedule in db_schedules:
                timeslots.append(TimeSlot(
                    id=schedule.id,
                    day_of_week=schedule.day_of_week,
                    start_time=schedule.start_time,
                    end_time=schedule.end_time
                ))
            
            from app.repositories.subject_repository import SubjectRepository
            subject_repo = SubjectRepository(db)
            subject = subject_repo.get_by_id(db_section.subject_id)
            
            sections.append(Section(
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
            ))
        
        if not sections:
            return None
        
        fitness_calc = ScheduleFitness(sections)
        return fitness_calc._calculate_gaps_penalty()
    
    gaps_none = get_gaps_penalty(db, solution_none)
    gaps_high = get_gaps_penalty(db, solution_high)
    
    print(f"\n📊 Resultados:")
    print(f"   Sin optimización: {gaps_none:.2f} puntos de penalización")
    print(f"   Con optimización: {gaps_high:.2f} puntos de penalización")
    
    if gaps_none and gaps_high:
        improvement = gaps_none - gaps_high
        if improvement > 0:
            print(f"   ✅ Mejora: {improvement:.2f} puntos (gaps reducidos)")
        elif improvement == 0:
            print(f"   ℹ️  Sin cambio: Los gaps ya eran mínimos")
        else:
            print(f"   ⚠️  Empeoró: {abs(improvement):.2f} puntos (revisar algoritmo)")


def test_balance_penalty(db: Session):
    """Prueba específica: Validación de penalización por desbalance"""
    print_section("PRUEBA ESPECÍFICA: Penalización por Desbalance")
    
    service = ScheduleService(db)
    student_repo = StudentRepository(db)
    subject_service = SubjectService(db)
    
    students = student_repo.get_all(limit=1)
    if not students:
        print("❌ No se encontraron estudiantes")
        return
    
    student = students[0]
    subjects = subject_service.get_subjects(program_id=student.program_id, limit=10)
    
    if not subjects:
        print("❌ No hay asignaturas disponibles")
        return
    
    selected_subject_ids = [s.id for s in subjects[:8]]
    
    print(f"\n📚 Objetivo: Validar que la optimización mejora el balance de días")
    print(f"   Asignaturas: {len(selected_subject_ids)}")
    
    solution_none = service.generate_schedule_for_student(
        student_id=student.id,
        selected_subject_ids=selected_subject_ids,
        optimization_level="none"
    )
    
    solution_high = service.generate_schedule_for_student(
        student_id=student.id,
        selected_subject_ids=selected_subject_ids,
        optimization_level="high"
    )
    
    def get_balance_penalty(db, solution):
        if not solution.is_feasible or not solution.assigned_section_ids:
            return None, None
        
        section_repo = CourseSectionRepository(db)
        sections = []
        
        for section_id in solution.assigned_section_ids:
            db_section = section_repo.get_by_id(section_id)
            if not db_section:
                continue
            
            db_schedules = db.query(SectionSchedule).filter(
                SectionSchedule.section_id == db_section.id
            ).all()
            
            timeslots = []
            for schedule in db_schedules:
                timeslots.append(TimeSlot(
                    id=schedule.id,
                    day_of_week=schedule.day_of_week,
                    start_time=schedule.start_time,
                    end_time=schedule.end_time
                ))
            
            from app.repositories.subject_repository import SubjectRepository
            subject_repo = SubjectRepository(db)
            subject = subject_repo.get_by_id(db_section.subject_id)
            
            sections.append(Section(
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
            ))
        
        if not sections:
            return None, None
        
        fitness_calc = ScheduleFitness(sections)
        balance_penalty = fitness_calc._calculate_balance_penalty()
        
        # Calcular distribución de días
        days_with_classes = set()
        for section in sections:
            for ts in section.timeslots:
                days_with_classes.add(ts.day_of_week)
        
        return balance_penalty, len(days_with_classes)
    
    balance_none, days_none = get_balance_penalty(db, solution_none)
    balance_high, days_high = get_balance_penalty(db, solution_high)
    
    print(f"\n📊 Resultados:")
    print(f"   Sin optimización: Penalización {balance_none:.2f}, Días con clases: {days_none}")
    print(f"   Con optimización: Penalización {balance_high:.2f}, Días con clases: {days_high}")
    
    if balance_none and balance_high:
        improvement = balance_none - balance_high
        if improvement > 0:
            print(f"   ✅ Mejora: {improvement:.2f} puntos (mejor balance)")
        elif improvement == 0:
            print(f"   ℹ️  Sin cambio: El balance ya era óptimo")
        else:
            print(f"   ⚠️  Empeoró: {abs(improvement):.2f} puntos")


def test_time_preference_penalty(db: Session):
    """Prueba específica: Validación de preferencias de horario"""
    print_section("PRUEBA ESPECÍFICA: Preferencias de Horario")
    
    service = ScheduleService(db)
    student_repo = StudentRepository(db)
    subject_service = SubjectService(db)
    
    students = student_repo.get_all(limit=1)
    if not students:
        print("❌ No se encontraron estudiantes")
        return
    
    student = students[0]
    subjects = subject_service.get_subjects(program_id=student.program_id, limit=8)
    
    if not subjects:
        print("❌ No hay asignaturas disponibles")
        return
    
    selected_subject_ids = [s.id for s in subjects[:6]]
    
    print(f"\n📚 Objetivo: Validar que la optimización evita horarios no preferidos")
    print(f"   Preferido: 8am-6pm")
    print(f"   No deseado: < 7am o > 6pm")
    
    solution_none = service.generate_schedule_for_student(
        student_id=student.id,
        selected_subject_ids=selected_subject_ids,
        optimization_level="none"
    )
    
    solution_high = service.generate_schedule_for_student(
        student_id=student.id,
        selected_subject_ids=selected_subject_ids,
        optimization_level="high"
    )
    
    def get_time_preference_penalty(db, solution):
        if not solution.is_feasible or not solution.assigned_section_ids:
            return None, []
        
        section_repo = CourseSectionRepository(db)
        sections = []
        early_late_classes = []
        
        for section_id in solution.assigned_section_ids:
            db_section = section_repo.get_by_id(section_id)
            if not db_section:
                continue
            
            db_schedules = db.query(SectionSchedule).filter(
                SectionSchedule.section_id == db_section.id
            ).all()
            
            timeslots = []
            for schedule in db_schedules:
                ts = TimeSlot(
                    id=schedule.id,
                    day_of_week=schedule.day_of_week,
                    start_time=schedule.start_time,
                    end_time=schedule.end_time
                )
                timeslots.append(ts)
                
                # Detectar horarios no preferidos
                if ts.start_time < time(7, 0) or ts.start_time >= time(18, 0):
                    early_late_classes.append(ts.start_time.strftime("%H:%M"))
            
            from app.repositories.subject_repository import SubjectRepository
            subject_repo = SubjectRepository(db)
            subject = subject_repo.get_by_id(db_section.subject_id)
            
            sections.append(Section(
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
            ))
        
        if not sections:
            return None, []
        
        fitness_calc = ScheduleFitness(sections)
        penalty = fitness_calc._calculate_time_preference_penalty()
        
        return penalty, early_late_classes
    
    penalty_none, classes_none = get_time_preference_penalty(db, solution_none)
    penalty_high, classes_high = get_time_preference_penalty(db, solution_high)
    
    print(f"\n📊 Resultados:")
    print(f"   Sin optimización: Penalización {penalty_none:.2f}, Horarios no preferidos: {len(classes_none)}")
    if classes_none:
        print(f"      Horarios: {', '.join(classes_none)}")
    print(f"   Con optimización: Penalización {penalty_high:.2f}, Horarios no preferidos: {len(classes_high)}")
    if classes_high:
        print(f"      Horarios: {', '.join(classes_high)}")
    
    if penalty_none and penalty_high:
        improvement = penalty_none - penalty_high
        if improvement > 0:
            print(f"   ✅ Mejora: {improvement:.2f} puntos (menos horarios no preferidos)")
        elif improvement == 0:
            print(f"   ℹ️  Sin cambio: Ya no hay horarios no preferidos o no se pueden evitar")


def test_consistency(db: Session):
    """Prueba específica: Consistencia de resultados"""
    print_section("PRUEBA ESPECÍFICA: Consistencia de Resultados")
    
    service = ScheduleService(db)
    student_repo = StudentRepository(db)
    subject_service = SubjectService(db)
    
    students = student_repo.get_all(limit=1)
    if not students:
        print("❌ No se encontraron estudiantes")
        return
    
    student = students[0]
    subjects = subject_service.get_subjects(program_id=student.program_id, limit=6)
    
    if not subjects:
        print("❌ No hay asignaturas disponibles")
        return
    
    selected_subject_ids = [s.id for s in subjects[:5]]
    
    print(f"\n📚 Objetivo: Validar que el algoritmo produce resultados consistentes")
    print(f"   Ejecutando 5 veces el mismo input...")
    
    results = []
    for i in range(5):
        solution = service.generate_schedule_for_student(
            student_id=student.id,
            selected_subject_ids=selected_subject_ids,
            optimization_level="medium"
        )
        
        results.append({
            "assigned_count": len(solution.assigned_subject_ids),
            "quality_score": solution.quality_score,
            "processing_time": solution.processing_time,
            "assigned_section_ids": sorted(solution.assigned_section_ids)
        })
    
    # Analizar consistencia
    assigned_counts = [r["assigned_count"] for r in results]
    quality_scores = [r["quality_score"] for r in results if r["quality_score"] is not None]
    processing_times = [r["processing_time"] for r in results]
    
    print(f"\n📊 Resultados:")
    print(f"   Asignaturas asignadas: {assigned_counts}")
    print(f"   Quality scores: {[f'{s:.2f}' for s in quality_scores]}")
    print(f"   Tiempos (s): {[f'{t:.3f}' for t in processing_times]}")
    
    # Verificar consistencia
    all_same_count = len(set(assigned_counts)) == 1
    all_same_sections = len(set(tuple(r["assigned_section_ids"]) for r in results)) == 1
    
    if all_same_count:
        print(f"   ✅ Consistente: Mismo número de asignaturas en todas las ejecuciones")
    else:
        print(f"   ⚠️  Inconsistente: Diferente número de asignaturas ({min(assigned_counts)}-{max(assigned_counts)})")
    
    if all_same_sections:
        print(f"   ✅ Consistente: Mismas secciones asignadas en todas las ejecuciones")
    else:
        print(f"   ⚠️  Variación: Diferentes secciones (pero mismo número de asignaturas)")
        print(f"      Esto es normal en algoritmos genéticos (múltiples soluciones óptimas)")
    
    if quality_scores:
        score_variance = max(quality_scores) - min(quality_scores)
        if score_variance < 1.0:
            print(f"   ✅ Consistente: Quality scores similares (varianza: {score_variance:.2f})")
        else:
            print(f"   ⚠️  Variación: Quality scores diferentes (varianza: {score_variance:.2f})")


def test_hard_constraints_preserved(db: Session):
    """Prueba específica: Validar que las restricciones duras se mantienen"""
    print_section("PRUEBA ESPECÍFICA: Restricciones Duras Preservadas")
    
    service = ScheduleService(db)
    student_repo = StudentRepository(db)
    subject_service = SubjectService(db)
    
    students = student_repo.get_all(limit=1)
    if not students:
        print("❌ No se encontraron estudiantes")
        return
    
    student = students[0]
    subjects = subject_service.get_subjects(program_id=student.program_id, limit=8)
    
    if not subjects:
        print("❌ No hay asignaturas disponibles")
        return
    
    selected_subject_ids = [s.id for s in subjects[:6]]
    
    print(f"\n📚 Objetivo: Validar que después de la optimización, las restricciones duras se mantienen")
    print(f"   Restricciones duras:")
    print(f"   - Sin choques de horario")
    print(f"   - Una sección por asignatura")
    print(f"   - Cupos disponibles")
    
    solution = service.generate_schedule_for_student(
        student_id=student.id,
        selected_subject_ids=selected_subject_ids,
        optimization_level="high"
    )
    
    if not solution.is_feasible:
        print("   ❌ Solución no factible")
        return
    
    # Validar restricciones
    section_repo = CourseSectionRepository(db)
    sections = []
    
    for section_id in solution.assigned_section_ids:
        db_section = section_repo.get_by_id(section_id)
        if not db_section:
            continue
        
        db_schedules = db.query(SectionSchedule).filter(
            SectionSchedule.section_id == db_section.id
        ).all()
        
        timeslots = []
        for schedule in db_schedules:
            timeslots.append(TimeSlot(
                id=schedule.id,
                day_of_week=schedule.day_of_week,
                start_time=schedule.start_time,
                end_time=schedule.end_time
            ))
        
        from app.repositories.subject_repository import SubjectRepository
        subject_repo = SubjectRepository(db)
        subject = subject_repo.get_by_id(db_section.subject_id)
        
        sections.append(Section(
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
        ))
    
    # Validar: una sección por asignatura
    subject_ids = [s.subject_id for s in sections]
    unique_subject_ids = set(subject_ids)
    
    print(f"\n📊 Validación:")
    print(f"   Asignaturas únicas: {len(unique_subject_ids)}/{len(selected_subject_ids)}")
    
    if len(subject_ids) == len(unique_subject_ids):
        print(f"   ✅ Una sección por asignatura: OK")
    else:
        print(f"   ❌ Violación: Múltiples secciones de la misma asignatura")
    
    # Validar: sin choques de horario
    conflicts = []
    for i, section_a in enumerate(sections):
        for section_b in sections[i+1:]:
            if section_a.has_time_overlap_with(section_b):
                conflicts.append((section_a.id, section_b.id))
    
    if not conflicts:
        print(f"   ✅ Sin choques de horario: OK")
    else:
        print(f"   ❌ Violación: {len(conflicts)} choques de horario detectados")
        for sec_a, sec_b in conflicts[:3]:
            print(f"      Sección {sec_a} choca con sección {sec_b}")
    
    # Validar: cupos disponibles
    no_capacity = [s for s in sections if s.available_spots <= 0]
    if not no_capacity:
        print(f"   ✅ Cupos disponibles: OK")
    else:
        print(f"   ❌ Violación: {len(no_capacity)} secciones sin cupos")
    
    if len(subject_ids) == len(unique_subject_ids) and not conflicts and not no_capacity:
        print(f"\n   ✅ TODAS LAS RESTRICCIONES DURAS SE MANTIENEN CORRECTAMENTE")


def test_free_days_bonus(db: Session):
    """Prueba específica: Validación de bonus por días libres"""
    print_section("PRUEBA ESPECÍFICA: Bonus por Días Libres")
    
    service = ScheduleService(db)
    student_repo = StudentRepository(db)
    subject_service = SubjectService(db)
    
    students = student_repo.get_all(limit=1)
    if not students:
        print("❌ No se encontraron estudiantes")
        return
    
    student = students[0]
    subjects = subject_service.get_subjects(program_id=student.program_id, limit=6)
    
    if not subjects:
        print("❌ No hay asignaturas disponibles")
        return
    
    selected_subject_ids = [s.id for s in subjects[:5]]
    
    print(f"\n📚 Objetivo: Validar que la optimización maximiza días libres")
    print(f"   Bonus: -20 puntos por cada día completamente libre")
    
    solution_none = service.generate_schedule_for_student(
        student_id=student.id,
        selected_subject_ids=selected_subject_ids,
        optimization_level="none"
    )
    
    solution_high = service.generate_schedule_for_student(
        student_id=student.id,
        selected_subject_ids=selected_subject_ids,
        optimization_level="high"
    )
    
    def get_free_days_info(db, solution):
        if not solution.is_feasible or not solution.assigned_section_ids:
            return None, None
        
        section_repo = CourseSectionRepository(db)
        sections = []
        
        for section_id in solution.assigned_section_ids:
            db_section = section_repo.get_by_id(section_id)
            if not db_section:
                continue
            
            db_schedules = db.query(SectionSchedule).filter(
                SectionSchedule.section_id == db_section.id
            ).all()
            
            timeslots = []
            for schedule in db_schedules:
                timeslots.append(TimeSlot(
                    id=schedule.id,
                    day_of_week=schedule.day_of_week,
                    start_time=schedule.start_time,
                    end_time=schedule.end_time
                ))
            
            from app.repositories.subject_repository import SubjectRepository
            subject_repo = SubjectRepository(db)
            subject = subject_repo.get_by_id(db_section.subject_id)
            
            sections.append(Section(
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
            ))
        
        if not sections:
            return None, None
        
        fitness_calc = ScheduleFitness(sections)
        bonus = fitness_calc._calculate_free_days_bonus()
        
        days_with_classes = set()
        for section in sections:
            for ts in section.timeslots:
                days_with_classes.add(ts.day_of_week)
        
        free_days = 7 - len(days_with_classes)
        
        return bonus, free_days
    
    bonus_none, free_days_none = get_free_days_info(db, solution_none)
    bonus_high, free_days_high = get_free_days_info(db, solution_high)
    
    print(f"\n📊 Resultados:")
    print(f"   Sin optimización: Bonus {bonus_none:.2f}, Días libres: {free_days_none}")
    print(f"   Con optimización: Bonus {bonus_high:.2f}, Días libres: {free_days_high}")
    
    if bonus_none and bonus_high:
        improvement = bonus_high - bonus_none  # Más negativo = mejor
        if improvement < 0:
            print(f"   ✅ Mejora: {abs(improvement):.2f} puntos más de bonus ({free_days_high - free_days_none} días libres adicionales)")
        elif improvement == 0:
            print(f"   ℹ️  Sin cambio: Mismo número de días libres")
        else:
            print(f"   ⚠️  Empeoró: {improvement:.2f} puntos menos de bonus")


def main():
    """Función principal"""
    print("\n" + "=" * 80)
    print("  🧪 PRUEBAS ESPECÍFICAS DEL ALGORITMO DE OPTIMIZACIÓN")
    print("=" * 80)
    print(f"\n⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    db: Session = SessionLocal()
    
    try:
        # Ejecutar todas las pruebas específicas
        test_gaps_penalty(db)
        test_balance_penalty(db)
        test_time_preference_penalty(db)
        test_free_days_bonus(db)
        test_consistency(db)
        test_hard_constraints_preserved(db)
        
        print_section("PRUEBAS ESPECÍFICAS COMPLETADAS")
        print(f"\n⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n✅ Todas las pruebas específicas se ejecutaron correctamente")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()


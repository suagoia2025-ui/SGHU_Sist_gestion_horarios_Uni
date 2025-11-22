#!/usr/bin/env python3
"""
Script avanzado para pruebas exhaustivas del algoritmo de optimización
Incluye: validación de restricciones blandas, casos con conflictos, análisis detallado
"""
import sys
from pathlib import Path

# Agregar el directorio backend al path
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


def analyze_schedule_quality(db: Session, solution, selected_subject_ids: list):
    """Analiza la calidad del horario generado"""
    from app.services.schedule_engine.models import Section, TimeSlot
    from app.services.schedule_engine.fitness import ScheduleFitness
    from app.repositories.subject_repository import CourseSectionRepository
    
    if not solution.is_feasible or not solution.assigned_section_ids:
        return None
    
    # Cargar secciones asignadas
    section_repo = CourseSectionRepository(db)
    sections = []
    
    for section_id in solution.assigned_section_ids:
        db_section = section_repo.get_by_id(section_id)
        if not db_section:
            continue
        
        # Cargar horarios
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
        
        # Obtener información de la asignatura
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
    
    # Calcular análisis detallado
    fitness_calc = ScheduleFitness(sections)
    breakdown = fitness_calc.get_fitness_breakdown()
    
    return breakdown


def test_fitness_breakdown(db: Session):
    """Prueba el análisis detallado de fitness"""
    print_section("PRUEBA: Análisis Detallado de Fitness")
    
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
    
    selected_subject_ids = [s.id for s in subjects[:6]]
    
    print(f"\n👤 Estudiante: {student.first_name} {student.last_name}")
    print(f"📚 Asignaturas seleccionadas: {len(selected_subject_ids)}")
    
    # Probar con diferentes niveles
    for level in ["none", "medium", "high"]:
        print(f"\n{'─' * 80}")
        print(f"🔧 Nivel de optimización: {level}")
        print(f"{'─' * 80}")
        
        try:
            solution = service.generate_schedule_for_student(
                student_id=student.id,
                selected_subject_ids=selected_subject_ids,
                optimization_level=level
            )
            
            if solution.is_feasible:
                breakdown = analyze_schedule_quality(db, solution, selected_subject_ids)
                
                if breakdown:
                    print(f"\n📊 Desglose de Fitness:")
                    print(f"   • Fitness Total: {breakdown['total_fitness']:.2f}")
                    print(f"   • Penalización por Gaps: {breakdown['gaps_penalty']:.2f}")
                    print(f"   • Penalización por Desbalance: {breakdown['balance_penalty']:.2f}")
                    print(f"   • Penalización por Horarios No Preferidos: {breakdown['time_preference_penalty']:.2f}")
                    print(f"   • Bonus por Días Libres: {breakdown['free_days_bonus']:.2f}")
                    print(f"\n📅 Estadísticas:")
                    print(f"   • Total de Slots: {breakdown['total_slots']}")
                    print(f"   • Días con Clases: {breakdown['days_with_classes']}")
                    print(f"   • Días Libres: {7 - breakdown['days_with_classes']}")
                else:
                    print("   ⚠️  No se pudo calcular el análisis detallado")
            else:
                print(f"   ❌ Solución no factible")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


def test_conflict_scenarios(db: Session):
    """Prueba escenarios con muchos conflictos"""
    print_section("PRUEBA: Escenarios con Conflictos")
    
    service = ScheduleService(db)
    student_repo = StudentRepository(db)
    subject_service = SubjectService(db)
    
    students = student_repo.get_all(limit=1)
    if not students:
        print("❌ No se encontraron estudiantes")
        return
    
    student = students[0]
    
    # Obtener muchas asignaturas para forzar conflictos
    subjects = subject_service.get_subjects(program_id=student.program_id, limit=15)
    
    if not subjects:
        print("❌ No hay asignaturas disponibles")
        return
    
    print(f"\n👤 Estudiante: {student.first_name} {student.last_name}")
    
    # Probar con diferentes cantidades de asignaturas
    test_cases = [
        (8, "Moderado"),
        (10, "Alto"),
        (12, "Muy Alto"),
        (15, "Máximo")
    ]
    
    for count, label in test_cases:
        selected_subject_ids = [s.id for s in subjects[:count]]
        
        print(f"\n{'─' * 80}")
        print(f"📚 Caso: {label} conflicto ({count} asignaturas)")
        print(f"{'─' * 80}")
        
        for level in ["none", "medium", "high"]:
            try:
                solution = service.generate_schedule_for_student(
                    student_id=student.id,
                    selected_subject_ids=selected_subject_ids,
                    optimization_level=level
                )
                
                assigned_count = len(solution.assigned_subject_ids)
                success_rate = (assigned_count / count) * 100
                
                print(f"   {level:8} → {assigned_count:2}/{count} asignadas ({success_rate:5.1f}%) | "
                      f"Tiempo: {solution.processing_time:.3f}s | "
                      f"Score: {solution.quality_score:.2f}" if solution.quality_score else f"Score: N/A")
                
            except Exception as e:
                print(f"   {level:8} → ❌ Error: {str(e)[:50]}")


def test_performance_benchmark(db: Session):
    """Prueba de rendimiento con múltiples ejecuciones"""
    print_section("PRUEBA: Benchmark de Rendimiento")
    
    service = ScheduleService(db)
    student_repo = StudentRepository(db)
    subject_service = SubjectService(db)
    
    students = student_repo.get_all(limit=3)
    if not students:
        print("❌ No se encontraron estudiantes")
        return
    
    subjects_by_student = {}
    for student in students:
        subjects = subject_service.get_subjects(program_id=student.program_id, limit=8)
        if subjects:
            subjects_by_student[student.id] = [s.id for s in subjects[:8]]
    
    if not subjects_by_student:
        print("❌ No hay asignaturas disponibles")
        return
    
    print(f"\n🔄 Ejecutando {len(students)} estudiantes × 4 niveles = {len(students) * 4} pruebas")
    print(f"   Niveles: none, low, medium, high")
    
    results = []
    
    for student in students:
        if student.id not in subjects_by_student:
            continue
        
        selected_subject_ids = subjects_by_student[student.id]
        
        for level in ["none", "low", "medium", "high"]:
            try:
                start_time = datetime.now()
                
                solution = service.generate_schedule_for_student(
                    student_id=student.id,
                    selected_subject_ids=selected_subject_ids,
                    optimization_level=level
                )
                
                end_time = datetime.now()
                elapsed = (end_time - start_time).total_seconds()
                
                results.append({
                    "student_id": student.id,
                    "level": level,
                    "assigned": len(solution.assigned_subject_ids),
                    "total": len(selected_subject_ids),
                    "time": elapsed,
                    "quality_score": solution.quality_score,
                    "feasible": solution.is_feasible
                })
                
            except Exception as e:
                results.append({
                    "student_id": student.id,
                    "level": level,
                    "error": str(e)
                })
    
    # Análisis de resultados
    print(f"\n{'─' * 80}")
    print("📊 Resumen de Rendimiento")
    print(f"{'─' * 80}")
    
    # Agrupar por nivel
    by_level = {}
    for r in results:
        if "error" not in r:
            level = r["level"]
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(r)
    
    print(f"\n{'Nivel':<10} {'Promedio (s)':<15} {'Mínimo (s)':<15} {'Máximo (s)':<15} {'Tasa Éxito':<15}")
    print("-" * 80)
    
    for level in ["none", "low", "medium", "high"]:
        if level in by_level:
            times = [r["time"] for r in by_level[level]]
            feasible_count = sum(1 for r in by_level[level] if r["feasible"])
            total_count = len(by_level[level])
            
            avg_time = sum(times) / len(times) if times else 0
            min_time = min(times) if times else 0
            max_time = max(times) if times else 0
            success_rate = (feasible_count / total_count * 100) if total_count > 0 else 0
            
            print(f"{level:<10} {avg_time:<15.3f} {min_time:<15.3f} {max_time:<15.3f} {success_rate:<15.1f}%")


def test_quality_comparison(db: Session):
    """Compara la calidad de soluciones con y sin optimización"""
    print_section("PRUEBA: Comparación de Calidad")
    
    service = ScheduleService(db)
    student_repo = StudentRepository(db)
    subject_service = SubjectService(db)
    
    students = student_repo.get_all(limit=5)
    if not students:
        print("❌ No se encontraron estudiantes")
        return
    
    print(f"\n🔄 Comparando soluciones con y sin optimización para {len(students)} estudiantes")
    
    improvements = []
    
    for student in students:
        subjects = subject_service.get_subjects(program_id=student.program_id, limit=7)
        if not subjects:
            continue
        
        selected_subject_ids = [s.id for s in subjects[:7]]
        
        # Sin optimización
        solution_none = service.generate_schedule_for_student(
            student_id=student.id,
            selected_subject_ids=selected_subject_ids,
            optimization_level="none"
        )
        
        # Con optimización
        solution_high = service.generate_schedule_for_student(
            student_id=student.id,
            selected_subject_ids=selected_subject_ids,
            optimization_level="high"
        )
        
        if solution_none.is_feasible and solution_high.is_feasible:
            score_none = solution_none.quality_score or float('inf')
            score_high = solution_high.quality_score or float('inf')
            
            if score_none != float('inf') and score_high != float('inf'):
                improvement = score_none - score_high  # Positivo = mejoró
                improvements.append({
                    "student_id": student.id,
                    "score_none": score_none,
                    "score_high": score_high,
                    "improvement": improvement,
                    "improvement_pct": (improvement / abs(score_none) * 100) if score_none != 0 else 0
                })
    
    if improvements:
        print(f"\n{'─' * 80}")
        print("📊 Resultados de Comparación")
        print(f"{'─' * 80}")
        
        print(f"\n{'Estudiante':<12} {'Sin Opt.':<12} {'Con Opt.':<12} {'Mejora':<12} {'Mejora %':<12}")
        print("-" * 80)
        
        for imp in improvements:
            print(f"{imp['student_id']:<12} "
                  f"{imp['score_none']:<12.2f} "
                  f"{imp['score_high']:<12.2f} "
                  f"{imp['improvement']:<12.2f} "
                  f"{imp['improvement_pct']:<12.1f}%")
        
        avg_improvement = sum(imp["improvement"] for imp in improvements) / len(improvements)
        avg_improvement_pct = sum(imp["improvement_pct"] for imp in improvements) / len(improvements)
        
        print(f"\n📈 Mejora promedio: {avg_improvement:.2f} puntos ({avg_improvement_pct:.1f}%)")
        
        if avg_improvement > 0:
            print("✅ La optimización genética mejora la calidad de los horarios")
        elif avg_improvement == 0:
            print("ℹ️  La optimización genética mantiene la calidad (solución ya óptima)")
        else:
            print("⚠️  La optimización genética empeora la calidad (revisar algoritmo)")


def main():
    """Función principal"""
    print("\n" + "=" * 80)
    print("  🧪 PRUEBAS AVANZADAS DEL ALGORITMO DE OPTIMIZACIÓN")
    print("=" * 80)
    print(f"\n⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    db: Session = SessionLocal()
    
    try:
        # Ejecutar todas las pruebas
        test_fitness_breakdown(db)
        test_conflict_scenarios(db)
        test_performance_benchmark(db)
        test_quality_comparison(db)
        
        print_section("PRUEBAS AVANZADAS COMPLETADAS")
        print(f"\n⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n✅ Todas las pruebas avanzadas se ejecutaron correctamente")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()


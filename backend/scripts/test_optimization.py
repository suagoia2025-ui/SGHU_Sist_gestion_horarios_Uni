#!/usr/bin/env python3
"""
Script para probar y validar el algoritmo de optimización de horarios
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
from app.repositories.subject_repository import AcademicPeriodRepository
import json
from datetime import datetime


def print_section(title: str):
    """Imprime un separador de sección"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_result(case_name: str, result: dict):
    """Imprime el resultado de una prueba"""
    print(f"\n📊 {case_name}")
    print("-" * 80)
    print(f"  ✅ Factible: {result['is_feasible']}")
    print(f"  📚 Asignaturas asignadas: {len(result['assigned_subject_ids'])}/{len(result.get('selected_subject_ids', []))}")
    print(f"  ⏱️  Tiempo de procesamiento: {result['processing_time']:.3f}s")
    print(f"  🎯 Quality Score: {result.get('quality_score', 'N/A')}")
    print(f"  🔧 Solver Status: {result['solver_status']}")
    
    if result['assigned_subject_ids']:
        print(f"\n  📖 Asignaturas asignadas:")
        for sub_id in result['assigned_subject_ids']:
            print(f"     - Subject ID: {sub_id}")
    
    if result.get('unassigned_subjects'):
        print(f"\n  ⚠️  Asignaturas no asignadas ({len(result['unassigned_subjects'])}):")
        for unassigned in result['unassigned_subjects'][:3]:  # Mostrar solo las primeras 3
            print(f"     - {unassigned['subject_code']}: {unassigned['reason']}")
        if len(result['unassigned_subjects']) > 3:
            print(f"     ... y {len(result['unassigned_subjects']) - 3} más")


def test_optimization_levels(db: Session, student_id: int, selected_subject_ids: list):
    """Prueba diferentes niveles de optimización"""
    print_section("PRUEBA: Comparación de Niveles de Optimización")
    
    service = ScheduleService(db)
    results = {}
    
    optimization_levels = ["none", "low", "medium", "high"]
    
    for level in optimization_levels:
        print(f"\n🔄 Probando nivel: {level}")
        try:
            solution = service.generate_schedule_for_student(
                student_id=student_id,
                selected_subject_ids=selected_subject_ids,
                optimization_level=level
            )
            
            results[level] = {
                "is_feasible": solution.is_feasible,
                "assigned_section_ids": solution.assigned_section_ids,
                "assigned_subject_ids": solution.assigned_subject_ids,
                "unassigned_subjects": [
                    {
                        "subject_id": u.subject_id,
                        "subject_code": u.subject_code,
                        "subject_name": u.subject_name,
                        "reason": u.reason
                    }
                    for u in solution.unassigned_subjects
                ],
                "processing_time": solution.processing_time,
                "quality_score": solution.quality_score,
                "solver_status": solution.solver_status,
                "selected_subject_ids": selected_subject_ids
            }
            
            print(f"   ✅ Completado: {len(solution.assigned_subject_ids)} asignaturas asignadas")
            print(f"   ⏱️  Tiempo: {solution.processing_time:.3f}s")
            print(f"   🎯 Quality Score: {solution.quality_score:.2f}" if solution.quality_score else "   🎯 Quality Score: N/A")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results[level] = {"error": str(e)}
    
    # Comparar resultados
    print_section("COMPARACIÓN DE RESULTADOS")
    
    print("\n📊 Resumen comparativo:")
    print(f"{'Nivel':<10} {'Factible':<10} {'Asignadas':<12} {'Tiempo (s)':<12} {'Quality Score':<15} {'Status':<20}")
    print("-" * 80)
    
    for level in optimization_levels:
        if "error" not in results[level]:
            r = results[level]
            feasible = "✅ Sí" if r["is_feasible"] else "❌ No"
            assigned = f"{len(r['assigned_subject_ids'])}/{len(selected_subject_ids)}"
            time_str = f"{r['processing_time']:.3f}"
            score_str = f"{r['quality_score']:.2f}" if r['quality_score'] else "N/A"
            status = r['solver_status']
            
            print(f"{level:<10} {feasible:<10} {assigned:<12} {time_str:<12} {score_str:<15} {status:<20}")
        else:
            print(f"{level:<10} {'❌ Error':<10} {'-':<12} {'-':<12} {'-':<15} {'-':<20}")
    
    # Encontrar mejor solución
    best_level = None
    best_score = float('inf')
    
    for level in optimization_levels:
        if "error" not in results[level] and results[level]["is_feasible"]:
            score = results[level]["quality_score"]
            if score is not None and score < best_score:
                best_score = score
                best_level = level
    
    if best_level:
        print(f"\n🏆 Mejor solución: {best_level} (Quality Score: {best_score:.2f})")
    
    return results


def test_different_students(db: Session):
    """Prueba con diferentes estudiantes"""
    print_section("PRUEBA: Diferentes Estudiantes")
    
    student_repo = StudentRepository(db)
    subject_service = SubjectService(db)
    period_repo = AcademicPeriodRepository(db)
    
    # Obtener algunos estudiantes
    students = student_repo.get_all(limit=5)
    
    if not students:
        print("❌ No se encontraron estudiantes en la base de datos")
        return
    
    period = period_repo.get_current()
    if not period:
        print("❌ No hay período académico activo")
        return
    
    service = ScheduleService(db)
    
    for i, student in enumerate(students[:3], 1):  # Probar con los primeros 3 estudiantes
        print(f"\n👤 Estudiante {i}: ID {student.id} - {student.first_name} {student.last_name}")
        print(f"   Programa: {student.program_id}")
        
        # Obtener asignaturas del programa del estudiante
        subjects = subject_service.get_subjects(program_id=student.program_id, limit=10)
        
        if not subjects:
            print("   ⚠️  No hay asignaturas disponibles para este programa")
            continue
        
        # Seleccionar algunas asignaturas (3-5)
        selected_subject_ids = [s.id for s in subjects[:min(5, len(subjects))]]
        
        print(f"   📚 Asignaturas seleccionadas: {len(selected_subject_ids)}")
        
        try:
            # Probar con optimización "medium"
            solution = service.generate_schedule_for_student(
                student_id=student.id,
                selected_subject_ids=selected_subject_ids,
                optimization_level="medium"
            )
            
            print(f"   ✅ Factible: {solution.is_feasible}")
            print(f"   📖 Asignaturas asignadas: {len(solution.assigned_subject_ids)}/{len(selected_subject_ids)}")
            print(f"   ⏱️  Tiempo: {solution.processing_time:.3f}s")
            print(f"   🎯 Quality Score: {solution.quality_score:.2f}" if solution.quality_score else "   🎯 Quality Score: N/A")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


def test_edge_cases(db: Session):
    """Prueba casos límite"""
    print_section("PRUEBA: Casos Límite")
    
    service = ScheduleService(db)
    student_repo = StudentRepository(db)
    
    # Obtener un estudiante
    students = student_repo.get_all(limit=1)
    if not students:
        print("❌ No se encontraron estudiantes")
        return
    
    student = students[0]
    
    # Caso 1: Muchas asignaturas (10+)
    print("\n📚 Caso 1: Muchas asignaturas seleccionadas")
    subject_service = SubjectService(db)
    subjects = subject_service.get_subjects(program_id=student.program_id, limit=15)
    
    if subjects:
        selected_subject_ids = [s.id for s in subjects[:10]]
        print(f"   Seleccionando {len(selected_subject_ids)} asignaturas...")
        
        try:
            solution = service.generate_schedule_for_student(
                student_id=student.id,
                selected_subject_ids=selected_subject_ids,
                optimization_level="medium"
            )
            
            print(f"   ✅ Factible: {solution.is_feasible}")
            print(f"   📖 Asignadas: {len(solution.assigned_subject_ids)}/{len(selected_subject_ids)}")
            print(f"   ⏱️  Tiempo: {solution.processing_time:.3f}s")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Caso 2: Pocas asignaturas (1-2)
    print("\n📚 Caso 2: Pocas asignaturas seleccionadas")
    if subjects:
        selected_subject_ids = [s.id for s in subjects[:2]]
        print(f"   Seleccionando {len(selected_subject_ids)} asignaturas...")
        
        try:
            solution = service.generate_schedule_for_student(
                student_id=student.id,
                selected_subject_ids=selected_subject_ids,
                optimization_level="high"
            )
            
            print(f"   ✅ Factible: {solution.is_feasible}")
            print(f"   📖 Asignadas: {len(solution.assigned_subject_ids)}/{len(selected_subject_ids)}")
            print(f"   ⏱️  Tiempo: {solution.processing_time:.3f}s")
            print(f"   🎯 Quality Score: {solution.quality_score:.2f}" if solution.quality_score else "   🎯 Quality Score: N/A")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


def main():
    """Función principal"""
    print("\n" + "=" * 80)
    print("  🧪 PRUEBAS DEL ALGORITMO DE OPTIMIZACIÓN DE HORARIOS")
    print("=" * 80)
    print(f"\n⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    db: Session = SessionLocal()
    
    try:
        # Obtener un estudiante y asignaturas para las pruebas
        student_repo = StudentRepository(db)
        subject_service = SubjectService(db)
        
        students = student_repo.get_all(limit=1)
        if not students:
            print("❌ No se encontraron estudiantes en la base de datos")
            return
        
        student = students[0]
        print(f"\n👤 Estudiante de prueba: ID {student.id} - {student.first_name} {student.last_name}")
        print(f"   Programa: {student.program_id}")
        
        # Obtener asignaturas del programa
        subjects = subject_service.get_subjects(program_id=student.program_id, limit=10)
        
        if not subjects:
            print("❌ No hay asignaturas disponibles para este programa")
            return
        
        selected_subject_ids = [s.id for s in subjects[:5]]  # Seleccionar 5 asignaturas
        print(f"📚 Asignaturas seleccionadas para pruebas: {len(selected_subject_ids)}")
        for s in subjects[:5]:
            print(f"   - {s.code}: {s.name}")
        
        # Ejecutar pruebas
        test_optimization_levels(db, student.id, selected_subject_ids)
        test_different_students(db)
        test_edge_cases(db)
        
        print_section("PRUEBAS COMPLETADAS")
        print(f"\n⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n✅ Todas las pruebas se ejecutaron correctamente")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()


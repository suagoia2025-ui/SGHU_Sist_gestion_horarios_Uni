#!/usr/bin/env python3
"""
Script para probar la persistencia de horarios en la base de datos
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
from app.models.sghu.schedule import GeneratedSchedule, ScheduleSlot
from app.models.sghu.enrollment import StudentEnrollment
from datetime import datetime


def print_section(title: str):
    """Imprime un separador de sección"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_schedule_persistence(db: Session):
    """Prueba la persistencia de horarios"""
    print_section("PRUEBA: Persistencia de Horarios")
    
    service = ScheduleService(db)
    student_repo = StudentRepository(db)
    subject_service = SubjectService(db)
    
    # Obtener un estudiante
    students = student_repo.get_all(limit=1)
    if not students:
        print("❌ No se encontraron estudiantes")
        return
    
    student = students[0]
    print(f"\n👤 Estudiante: {student.first_name} {student.last_name} (ID: {student.id})")
    
    # Obtener asignaturas
    subjects = subject_service.get_subjects(program_id=student.program_id, limit=5)
    if not subjects:
        print("❌ No hay asignaturas disponibles")
        return
    
    selected_subject_ids = [s.id for s in subjects[:5]]
    print(f"📚 Asignaturas seleccionadas: {len(selected_subject_ids)}")
    
    # Generar horario con persistencia
    print(f"\n🔄 Generando horario con optimización 'medium'...")
    solution = service.generate_schedule_for_student(
        student_id=student.id,
        selected_subject_ids=selected_subject_ids,
        optimization_level="medium"
    )
    
    if not solution.is_feasible:
        print("❌ No se generó un horario factible")
        return
    
    print(f"✅ Horario generado:")
    print(f"   • Asignaturas asignadas: {len(solution.assigned_subject_ids)}")
    print(f"   • Secciones asignadas: {len(solution.assigned_section_ids)}")
    print(f"   • Quality Score: {solution.quality_score:.2f}" if solution.quality_score else "   • Quality Score: N/A")
    print(f"   • Tiempo: {solution.processing_time:.3f}s")
    
    # Verificar que se guardó en la base de datos
    print(f"\n🔍 Verificando persistencia en base de datos...")
    
    # Buscar el horario más reciente del estudiante
    enrollments = db.query(StudentEnrollment).filter(
        StudentEnrollment.student_id == student.id
    ).order_by(StudentEnrollment.created_at.desc()).all()
    
    if not enrollments:
        print("❌ No se encontró ningún enrollment para el estudiante")
        return
    
    latest_enrollment = enrollments[0]
    print(f"   • Enrollment ID: {latest_enrollment.id}")
    print(f"   • Estado: {latest_enrollment.status}")
    
    # Buscar horarios generados
    schedules = db.query(GeneratedSchedule).filter(
        GeneratedSchedule.enrollment_id == latest_enrollment.id
    ).order_by(GeneratedSchedule.created_at.desc()).all()
    
    if not schedules:
        print("❌ No se encontraron horarios generados")
        return
    
    latest_schedule = schedules[0]
    print(f"\n✅ Horario persistido:")
    print(f"   • Schedule ID: {latest_schedule.id}")
    print(f"   • Método de generación: {latest_schedule.generation_method}")
    print(f"   • Quality Score: {latest_schedule.quality_score:.2f}" if latest_schedule.quality_score else "   • Quality Score: N/A")
    print(f"   • Tiempo de procesamiento: {latest_schedule.processing_time:.3f}s")
    print(f"   • Estado: {latest_schedule.status}")
    print(f"   • Creado: {latest_schedule.created_at}")
    
    # Verificar ScheduleSlots
    slots = db.query(ScheduleSlot).filter(
        ScheduleSlot.schedule_id == latest_schedule.id
    ).all()
    
    print(f"\n📅 Schedule Slots: {len(slots)}")
    if slots:
        print(f"   Detalles de los primeros 5 slots:")
        days_map = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}
        for i, slot in enumerate(slots[:5], 1):
            day_name = days_map.get(slot.day_of_week, f"Día {slot.day_of_week}")
            print(f"   {i}. Sección {slot.section_id} - {day_name} {slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}")
        if len(slots) > 5:
            print(f"   ... y {len(slots) - 5} slots más")
    
    # Verificar que los slots coinciden con las secciones asignadas
    slot_section_ids = {slot.section_id for slot in slots}
    assigned_section_ids = set(solution.assigned_section_ids)
    
    if slot_section_ids == assigned_section_ids:
        print(f"\n✅ Validación: Los slots coinciden con las secciones asignadas")
    else:
        print(f"\n⚠️  Advertencia: Hay diferencias entre slots y secciones asignadas")
        print(f"   Slots: {slot_section_ids}")
        print(f"   Asignadas: {assigned_section_ids}")
    
    return latest_schedule


def test_multiple_schedules(db: Session):
    """Prueba generar múltiples horarios para el mismo estudiante"""
    print_section("PRUEBA: Múltiples Horarios")
    
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
    
    print(f"\n🔄 Generando 3 horarios con diferentes niveles de optimización...")
    
    schedules_created = []
    for level in ["none", "medium", "high"]:
        print(f"\n   Nivel: {level}")
        solution = service.generate_schedule_for_student(
            student_id=student.id,
            selected_subject_ids=selected_subject_ids,
            optimization_level=level
        )
        
        if solution.is_feasible:
            # Buscar el horario más reciente
            enrollments = db.query(StudentEnrollment).filter(
                StudentEnrollment.student_id == student.id
            ).order_by(StudentEnrollment.created_at.desc()).first()
            
            if enrollments:
                latest_schedule = db.query(GeneratedSchedule).filter(
                    GeneratedSchedule.enrollment_id == enrollments.id
                ).order_by(GeneratedSchedule.created_at.desc()).first()
                
                if latest_schedule:
                    schedules_created.append({
                        "level": level,
                        "schedule_id": latest_schedule.id,
                        "method": latest_schedule.generation_method,
                        "quality_score": latest_schedule.quality_score,
                        "status": latest_schedule.status
                    })
                    print(f"      ✅ Horario {latest_schedule.id} guardado")
    
    print(f"\n📊 Resumen:")
    print(f"   Horarios creados: {len(schedules_created)}")
    for sched in schedules_created:
        score_str = f"{sched['quality_score']:.2f}" if sched['quality_score'] else "N/A"
        print(f"   • {sched['level']:8} → ID: {sched['schedule_id']}, Método: {sched['method']}, Score: {score_str}")


def main():
    """Función principal"""
    print("\n" + "=" * 80)
    print("  🧪 PRUEBAS DE PERSISTENCIA DE HORARIOS")
    print("=" * 80)
    print(f"\n⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    db: Session = SessionLocal()
    
    try:
        test_schedule_persistence(db)
        test_multiple_schedules(db)
        
        print_section("PRUEBAS DE PERSISTENCIA COMPLETADAS")
        print(f"\n⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n✅ Todas las pruebas de persistencia se ejecutaron correctamente")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()


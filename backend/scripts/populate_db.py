"""
Script maestro que ejecuta todos los simuladores en orden correcto.
"""
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import argparse
from sqlalchemy import text
from app.database import SessionLocal, engine
from scripts.simulate_odoo import OdooSimulator
from scripts.simulate_students import StudentSimulator
from scripts.simulate_offer import OfferSimulator


def clean_database(db, confirm: bool = False):
    """Limpia la base de datos (opcional)"""
    if not confirm:
        print("⚠️  Para limpiar la BD, usa --clean-db")
        return
    
    print("🧹 Limpiando base de datos...")
    
    # Orden de eliminación respetando foreign keys
    tables_to_clean = [
        # Schema sghu (primero)
        'sghu.processing_logs',
        'sghu.schedule_conflicts',
        'sghu.schedule_slots',
        'sghu.generated_schedules',
        'sghu.enrollment_subjects',
        'sghu.student_enrollments',
        'sghu.enrollment_periods',
        # Schema source
        'source.moodle_enrollments',
        'source.moodle_courses',
        'source.section_schedules',
        'source.course_sections',
        'source.academic_periods',
        'source.financial_status',
        'source.academic_history',
        'source.students',
        'source.prerequisites',
        'source.study_plans',
        'source.subjects',
        'source.programs',
        'source.professors',
        'source.classrooms',
        'source.academic_rules',
    ]
    
    for table in tables_to_clean:
        try:
            db.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
            print(f"  ✅ Limpiada: {table}")
        except Exception as e:
            print(f"  ⚠️  Error limpiando {table}: {e}")
    
    db.commit()
    print("✅ Base de datos limpiada\n")


def validate_integrity(db):
    """Valida integridad referencial de los datos"""
    print("\n🔍 Validando integridad de datos...")
    
    issues = []
    
    # Verificar que todos los programas tienen materias
    from app.models.source.academic import Program, Subject
    programs = db.query(Program).all()
    for program in programs:
        subjects_count = db.query(Subject).filter(Subject.program_id == program.id).count()
        if subjects_count == 0:
            issues.append(f"Programa {program.code} no tiene materias")
        elif subjects_count < 20:
            issues.append(f"Programa {program.code} tiene solo {subjects_count} materias (esperado 20)")
    
    # Verificar que hay profesores y aulas
    from app.models.source.people import Professor
    from app.models.source.infrastructure import Classroom
    professors_count = db.query(Professor).count()
    classrooms_count = db.query(Classroom).count()
    
    if professors_count < 30:
        issues.append(f"Solo hay {professors_count} profesores (esperado 30+)")
    if classrooms_count < 20:
        issues.append(f"Solo hay {classrooms_count} aulas (esperado 20+)")
    
    # Verificar estudiantes
    from app.models.source.people import Student
    students_count = db.query(Student).count()
    if students_count == 0:
        issues.append("No hay estudiantes creados")
    
    if issues:
        print("  ⚠️  Problemas encontrados:")
        for issue in issues:
            print(f"    - {issue}")
        return False
    else:
        print("  ✅ Integridad validada correctamente")
        return True


def generate_report(db):
    """Genera reporte de datos creados"""
    print("\n📊 Generando reporte de datos...")
    
    from app.models.source.academic import Program, Subject, StudyPlan, Prerequisite
    from app.models.source.people import Student, Professor
    from app.models.source.infrastructure import Classroom
    from app.models.source.student_data import AcademicHistory, FinancialStatus
    from app.models.source.offer import AcademicPeriod, CourseSection, SectionSchedule
    from app.models.source.rules import AcademicRule
    
    stats = {
        'Programas': db.query(Program).count(),
        'Asignaturas': db.query(Subject).count(),
        'Malla curricular': db.query(StudyPlan).count(),
        'Prerrequisitos': db.query(Prerequisite).count(),
        'Profesores': db.query(Professor).count(),
        'Aulas': db.query(Classroom).count(),
        'Reglas académicas': db.query(AcademicRule).count(),
        'Estudiantes': db.query(Student).count(),
        'Historial académico': db.query(AcademicHistory).count(),
        'Estados financieros': db.query(FinancialStatus).count(),
        'Períodos académicos': db.query(AcademicPeriod).count(),
        'Secciones': db.query(CourseSection).count(),
        'Horarios': db.query(SectionSchedule).count(),
    }
    
    print("\n" + "="*50)
    print("REPORTE DE DATOS GENERADOS")
    print("="*50)
    for key, value in stats.items():
        print(f"  {key:.<30} {value:>10}")
    print("="*50)
    
    # Estadísticas adicionales
    print("\n📈 Estadísticas adicionales:")
    
    # Estudiantes por programa
    programs = db.query(Program).all()
    print("\n  Estudiantes por programa:")
    for program in programs:
        count = db.query(Student).filter(Student.program_id == program.id).count()
        print(f"    - {program.code}: {count} estudiantes")
    
    # Estudiantes con deuda
    students_with_debt = db.query(FinancialStatus).filter(FinancialStatus.has_debt == 'true').count()
    total_students = stats['Estudiantes']
    if total_students > 0:
        debt_percentage = (students_with_debt / total_students) * 100
        print(f"\n  Estudiantes con deuda: {students_with_debt} ({debt_percentage:.1f}%)")
    
    # Secciones por período
    periods = db.query(AcademicPeriod).all()
    print("\n  Secciones por período:")
    for period in periods:
        count = db.query(CourseSection).filter(CourseSection.period_id == period.id).count()
        print(f"    - {period.code}: {count} secciones")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Poblar base de datos con datos simulados')
    parser.add_argument('--clean-db', action='store_true', help='Limpiar BD antes de poblar')
    parser.add_argument('--num-students', type=int, default=200, help='Número de estudiantes a crear')
    parser.add_argument('--year', type=int, default=2025, help='Año del período académico')
    parser.add_argument('--cycle', type=int, default=1, choices=[1, 2], help='Ciclo (1=Feb-May, 2=Ago-Nov)')
    parser.add_argument('--skip-odoo', action='store_true', help='Omitir simulación de Odoo')
    parser.add_argument('--skip-students', action='store_true', help='Omitir simulación de estudiantes')
    parser.add_argument('--skip-offer', action='store_true', help='Omitir simulación de oferta')
    
    args = parser.parse_args()
    
    db = SessionLocal()
    
    try:
        # Limpiar BD si se solicita
        if args.clean_db:
            clean_database(db, confirm=True)
        
        results = {}
        
        # 1. Simular datos Odoo
        if not args.skip_odoo:
            print("\n" + "="*60)
            print("FASE 1: SIMULACIÓN DE DATOS ODOO")
            print("="*60)
            simulator_odoo = OdooSimulator(db)
            results['odoo'] = simulator_odoo.simulate_all()
        else:
            print("⏭️  Omitiendo simulación de Odoo")
        
        # 2. Simular estudiantes
        if not args.skip_students:
            print("\n" + "="*60)
            print("FASE 2: SIMULACIÓN DE ESTUDIANTES")
            print("="*60)
            simulator_students = StudentSimulator(db, args.num_students)
            results['students'] = simulator_students.simulate_all()
        else:
            print("⏭️  Omitiendo simulación de estudiantes")
        
        # 3. Simular oferta académica
        if not args.skip_offer:
            print("\n" + "="*60)
            print("FASE 3: SIMULACIÓN DE OFERTA ACADÉMICA")
            print("="*60)
            simulator_offer = OfferSimulator(db, args.year, args.cycle)
            results['offer'] = simulator_offer.simulate_all()
        else:
            print("⏭️  Omitiendo simulación de oferta académica")
        
        # 4. Validar integridad
        validate_integrity(db)
        
        # 5. Generar reporte
        generate_report(db)
        
        print("\n✅ Proceso completado exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


"""
Script para limpiar/resetear la base de datos completamente.
"""
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.database import SessionLocal


def reset_database(confirm: bool = False):
    """Limpia todas las tablas de la base de datos"""
    if not confirm:
        print("⚠️  Este script eliminará TODOS los datos de la BD.")
        print("⚠️  Para confirmar, usa --confirm")
        return
    
    db = SessionLocal()
    
    try:
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
        print("\n✅ Base de datos limpiada completamente")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Función principal"""
    import argparse
    parser = argparse.ArgumentParser(description='Resetear base de datos')
    parser.add_argument('--confirm', action='store_true', 
                       help='Confirmar limpieza de BD (requerido)')
    args = parser.parse_args()
    
    reset_database(args.confirm)


if __name__ == "__main__":
    main()


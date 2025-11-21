"""
Script para simular oferta académica:
- Períodos académicos (ciclos Feb-May y Ago-Nov)
- Secciones ofertadas
- Horarios de secciones (sin conflictos)
"""
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
import random
from datetime import datetime, date, time, timedelta

from app.database import SessionLocal
from app.models.source.offer import AcademicPeriod, CourseSection, SectionSchedule
from app.models.source.academic import Subject, StudyPlan
from app.models.source.people import Professor
from app.models.source.infrastructure import Classroom

random.seed(42)


class OfferSimulator:
    """Simulador de oferta académica"""
    
    def __init__(self, db: Session, period_year: int = 2025, period_cycle: int = 1):
        self.db = db
        self.period_year = period_year
        self.period_cycle = period_cycle  # 1 = Feb-May, 2 = Ago-Nov
        self.period = None
        self.sections_created = []
        self.schedules_created = []
    
    def simulate_all(self):
        """Ejecuta toda la simulación de oferta académica"""
        print("🚀 Iniciando simulación de oferta académica...")
        
        # Crear período académico
        print("\n📅 Creando período académico...")
        self._create_academic_period()
        
        # Generar secciones
        print("\n📚 Generando secciones...")
        self._create_sections()
        
        # Generar horarios
        print("\n⏰ Generando horarios de secciones...")
        self._create_schedules()
        
        self.db.commit()
        print("\n✅ Simulación de oferta académica completada exitosamente!")
        
        return {
            'period': self.period.code,
            'sections': len(self.sections_created),
            'schedules': len(self.schedules_created)
        }
    
    def _create_academic_period(self):
        """Crea período académico según ciclo"""
        if self.period_cycle == 1:
            # Primer ciclo: Febrero-Mayo
            start_date = date(self.period_year, 2, 1)
            end_date = date(self.period_year, 5, 31)
            enrollment_start = date(self.period_year - 1, 12, 1)
            enrollment_end = date(self.period_year, 1, 31)
            name = f"Primer Ciclo {self.period_year}"
        else:
            # Segundo ciclo: Agosto-Noviembre
            start_date = date(self.period_year, 8, 1)
            end_date = date(self.period_year, 11, 30)
            enrollment_start = date(self.period_year, 6, 1)
            enrollment_end = date(self.period_year, 7, 31)
            name = f"Segundo Ciclo {self.period_year}"
        
        code = f"{self.period_year}-{self.period_cycle}"
        
        self.period = AcademicPeriod(
            code=code,
            name=name,
            start_date=start_date,
            end_date=end_date,
            enrollment_start=enrollment_start,
            enrollment_end=enrollment_end,
            status='active'
        )
        self.db.add(self.period)
        self.db.flush()
        print(f"  ✅ Período {code} creado ({name})")
    
    def _create_sections(self):
        """Crea secciones para las materias del período"""
        # Obtener todas las materias
        subjects = self.db.query(Subject).all()
        
        # Obtener profesores y aulas
        professors = self.db.query(Professor).all()
        classrooms = self.db.query(Classroom).all()
        
        if not professors or not classrooms:
            raise ValueError("No hay profesores o aulas disponibles. Ejecuta simulate_odoo.py primero.")
        
        # Determinar qué materias ofertar según el ciclo
        # En cada ciclo se ofertan materias de 2 semestres
        # Ciclo 1: Semestres 1 y 2
        # Ciclo 2: Semestres 3 y 4
        
        if self.period_cycle == 1:
            target_semesters = [1, 2]
        else:
            target_semesters = [3, 4]
        
        # Obtener materias de los semestres objetivo
        study_plans = self.db.query(StudyPlan).filter(
            StudyPlan.semester.in_(target_semesters)
        ).all()
        
        subjects_to_offer = {plan.subject_id for plan in study_plans}
        
        section_number = 1
        
        for subject in subjects:
            if subject.id not in subjects_to_offer:
                continue
            
            # Determinar cuántas secciones crear (1-3 según popularidad)
            # Materias básicas tienen más secciones
            num_sections = random.choices([1, 2, 3], weights=[30, 50, 20])[0]
            
            for section_num in range(1, num_sections + 1):
                # Seleccionar profesor aleatorio
                professor = random.choice(professors)
                
                # Seleccionar aula apropiada
                # Aulas grandes para auditorios, normales para teoría, pequeñas para práctica
                if 'laboratorio' in subject.name.lower() or 'práctica' in subject.name.lower():
                    suitable_classrooms = [c for c in classrooms if c.type == 'laboratorio']
                elif subject.theory_hours > subject.practice_hours:
                    suitable_classrooms = [c for c in classrooms if c.type in ['aula', 'auditorio']]
                else:
                    suitable_classrooms = classrooms
                
                if not suitable_classrooms:
                    suitable_classrooms = [c for c in classrooms if c.capacity >= 30]
                
                classroom = random.choice(suitable_classrooms)
                
                # Capacidad según tipo de aula y materia
                if classroom.type == 'auditorio':
                    capacity = random.randint(80, classroom.capacity)
                elif classroom.type == 'laboratorio':
                    capacity = random.randint(15, classroom.capacity)
                else:
                    capacity = random.randint(25, classroom.capacity)
                
                section = CourseSection(
                    period_id=self.period.id,
                    subject_id=subject.id,
                    section_number=section_num,
                    professor_id=professor.id,
                    capacity=capacity,
                    enrolled_count=0,
                    classroom_id=classroom.id
                )
                self.db.add(section)
                self.sections_created.append(section)
                section_number += 1
        
        self.db.flush()
        print(f"  ✅ {len(self.sections_created)} secciones creadas")
    
    def _create_schedules(self):
        """Crea horarios para las secciones sin conflictos"""
        days_of_week = list(range(6))  # Lunes (0) a Sábado (5)
        
        # Bloques horarios comunes
        time_blocks = [
            (time(7, 0), time(9, 0)),   # 7:00-9:00
            (time(9, 0), time(11, 0)),  # 9:00-11:00
            (time(11, 0), time(13, 0)), # 11:00-13:00
            (time(14, 0), time(16, 0)), # 14:00-16:00
            (time(16, 0), time(18, 0)), # 16:00-18:00
            (time(18, 0), time(20, 0)), # 18:00-20:00
        ]
        
        # Rastrear horarios ocupados por profesor y aula
        professor_schedules = {}  # {professor_id: [(day, start, end), ...]}
        classroom_schedules = {}  # {classroom_id: [(day, start, end), ...]}
        
        for section in self.sections_created:
            # Determinar número de sesiones por semana según créditos
            # 4 créditos = 2 horas semanales = 1 sesión de 2 horas o 2 sesiones de 1 hora
            num_sessions = 1 if section.subject.credits == 4 else 2
            
            # Seleccionar días y horarios
            selected_slots = []
            attempts = 0
            max_attempts = 100
            
            while len(selected_slots) < num_sessions and attempts < max_attempts:
                day = random.choice(days_of_week)
                start_time, end_time = random.choice(time_blocks)
                
                # Verificar conflictos con profesor
                prof_conflict = False
                if section.professor_id in professor_schedules:
                    for existing_day, existing_start, existing_end in professor_schedules[section.professor_id]:
                        if existing_day == day and self._times_overlap(start_time, end_time, existing_start, existing_end):
                            prof_conflict = True
                            break
                
                # Verificar conflictos con aula
                classroom_conflict = False
                if section.classroom_id in classroom_schedules:
                    for existing_day, existing_start, existing_end in classroom_schedules[section.classroom_id]:
                        if existing_day == day and self._times_overlap(start_time, end_time, existing_start, existing_end):
                            classroom_conflict = True
                            break
                
                # Si no hay conflictos, agregar
                if not prof_conflict and not classroom_conflict:
                    selected_slots.append((day, start_time, end_time))
                    
                    # Registrar en horarios ocupados
                    if section.professor_id not in professor_schedules:
                        professor_schedules[section.professor_id] = []
                    professor_schedules[section.professor_id].append((day, start_time, end_time))
                    
                    if section.classroom_id not in classroom_schedules:
                        classroom_schedules[section.classroom_id] = []
                    classroom_schedules[section.classroom_id].append((day, start_time, end_time))
                
                attempts += 1
            
            # Crear registros de horario
            for day, start_time, end_time in selected_slots:
                # Determinar tipo de sesión
                if section.subject.lab_hours > 0:
                    session_type = 'laboratorio'
                elif section.subject.practice_hours > section.subject.theory_hours:
                    session_type = 'práctica'
                else:
                    session_type = 'teoría'
                
                schedule = SectionSchedule(
                    section_id=section.id,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time,
                    session_type=session_type
                )
                self.db.add(schedule)
                self.schedules_created.append(schedule)
        
        self.db.flush()
        print(f"  ✅ {len(self.schedules_created)} horarios creados")
    
    def _times_overlap(self, start1: time, end1: time, start2: time, end2: time) -> bool:
        """Verifica si dos intervalos de tiempo se solapan"""
        return not (end1 <= start2 or end2 <= start1)


def main(period_year: int = 2025, period_cycle: int = 1):
    """Función principal"""
    db = SessionLocal()
    try:
        simulator = OfferSimulator(db, period_year, period_cycle)
        results = simulator.simulate_all()
        
        print("\n📊 Resumen de datos creados:")
        print(f"  - Período: {results['period']}")
        print(f"  - Secciones: {results['sections']}")
        print(f"  - Horarios: {results['schedules']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Simular oferta académica')
    parser.add_argument('--year', type=int, default=2025, help='Año del período')
    parser.add_argument('--cycle', type=int, default=1, choices=[1, 2], help='Ciclo (1=Feb-May, 2=Ago-Nov)')
    args = parser.parse_args()
    
    main(args.year, args.cycle)


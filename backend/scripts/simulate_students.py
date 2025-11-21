"""
Script para simular datos de estudiantes:
- Estudiantes (200+)
- Historial académico coherente
- Estados financieros
"""
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from faker import Faker
import random
from datetime import datetime, date, timedelta

from app.database import SessionLocal
from app.models.source.people import Student
from app.models.source.academic import Program, Subject, StudyPlan, Prerequisite
from app.models.source.student_data import AcademicHistory, FinancialStatus

fake = Faker('es_ES')
Faker.seed(42)
random.seed(42)


class StudentSimulator:
    """Simulador de datos de estudiantes"""
    
    def __init__(self, db: Session, num_students: int = 200):
        self.db = db
        self.num_students = num_students
        self.students_created = []
        self.programs = None
        self.subjects_by_program = {}
        self.study_plans_by_program = {}
        self.prerequisites_map = {}
    
    def simulate_all(self):
        """Ejecuta toda la simulación de estudiantes"""
        print("🚀 Iniciando simulación de estudiantes...")
        
        # Cargar datos necesarios
        self._load_programs()
        self._load_subjects()
        self._load_study_plans()
        self._load_prerequisites()
        
        # Crear estudiantes
        print(f"\n👥 Creando {self.num_students} estudiantes...")
        self._create_students()
        
        # Crear historial académico
        print("\n📚 Creando historial académico...")
        self._create_academic_history()
        
        # Crear estados financieros
        print("\n💰 Creando estados financieros...")
        self._create_financial_status()
        
        self.db.commit()
        print("\n✅ Simulación de estudiantes completada exitosamente!")
        
        return {
            'students': len(self.students_created),
            'academic_history': self._count_academic_history(),
            'financial_status': len(self.students_created)
        }
    
    def _load_programs(self):
        """Carga programas de la BD"""
        self.programs = self.db.query(Program).all()
        print(f"  ✅ {len(self.programs)} programas cargados")
    
    def _load_subjects(self):
        """Carga asignaturas agrupadas por programa"""
        subjects = self.db.query(Subject).all()
        for subject in subjects:
            if subject.program_id not in self.subjects_by_program:
                self.subjects_by_program[subject.program_id] = []
            self.subjects_by_program[subject.program_id].append(subject)
    
    def _load_study_plans(self):
        """Carga malla curricular agrupada por programa y semestre"""
        study_plans = self.db.query(StudyPlan).all()
        for plan in study_plans:
            if plan.program_id not in self.study_plans_by_program:
                self.study_plans_by_program[plan.program_id] = {}
            if plan.semester not in self.study_plans_by_program[plan.program_id]:
                self.study_plans_by_program[plan.program_id][plan.semester] = []
            self.study_plans_by_program[plan.program_id][plan.semester].append(plan)
    
    def _load_prerequisites(self):
        """Carga prerrequisitos en un mapa"""
        prerequisites = self.db.query(Prerequisite).all()
        for prereq in prerequisites:
            if prereq.subject_id not in self.prerequisites_map:
                self.prerequisites_map[prereq.subject_id] = []
            self.prerequisites_map[prereq.subject_id].append(prereq.prerequisite_subject_id)
    
    def _create_students(self):
        """Crea estudiantes distribuidos en programas y semestres"""
        students_per_program = self.num_students // len(self.programs)
        student_number = 1
        
        for program in self.programs:
            # Distribuir estudiantes en semestres (1-10)
            # Más estudiantes en semestres iniciales
            semester_distribution = [1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7, 8, 9, 10]
            
            for _ in range(students_per_program):
                current_semester = random.choice(semester_distribution)
                
                # Calcular fecha de admisión según semestre actual
                # Asumiendo que cada semestre = 2 ciclos (8 meses)
                cycles_completed = (current_semester - 1) * 2
                months_ago = cycles_completed * 4  # Cada ciclo = 4 meses
                admission_date = date.today() - timedelta(days=months_ago * 30)
                
                first_name = fake.first_name()
                last_name = fake.last_name()
                email = f"{first_name.lower()}.{last_name.lower()}{student_number}@estudiante.edu"
                
                # Asegurar email único
                existing_emails = {s.email for s in self.students_created}
                counter = 1
                while email in existing_emails:
                    email = f"{first_name.lower()}.{last_name.lower()}{student_number}{counter}@estudiante.edu"
                    counter += 1
                
                student = Student(
                    code=f"EST{student_number:05d}",
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    program_id=program.id,
                    current_semester=current_semester,
                    admission_date=admission_date
                )
                self.db.add(student)
                self.students_created.append(student)
                student_number += 1
        
        self.db.flush()
        print(f"  ✅ {len(self.students_created)} estudiantes creados")
    
    def _create_academic_history(self):
        """Crea historial académico coherente para cada estudiante"""
        history_count = 0
        
        for student in self.students_created:
            # Determinar qué materias debería haber cursado según semestre actual
            # Cada semestre = 2 ciclos = 10 materias (5 por ciclo)
            cycles_completed = (student.current_semester - 1) * 2
            
            if cycles_completed == 0:
                continue  # Estudiante de primer semestre sin historial
            
            # Obtener materias de la malla curricular
            program_plans = self.study_plans_by_program.get(student.program_id, {})
            
            # Recopilar todas las materias que debería haber cursado
            subjects_to_have_taken = []
            for semester in range(1, student.current_semester):
                if semester in program_plans:
                    for plan in program_plans[semester]:
                        subjects_to_have_taken.append(plan.subject)
            
            # Limitar a las materias que corresponden a los ciclos completados
            # Cada ciclo = 5 materias
            max_subjects = cycles_completed * 5
            subjects_to_have_taken = subjects_to_have_taken[:max_subjects]
            
            # Crear historial para cada materia
            approved_subjects = set()
            subject_index = 0  # Índice para asignar períodos
            
            for subject in subjects_to_have_taken:
                # Verificar prerrequisitos
                prereq_ids = self.prerequisites_map.get(subject.id, [])
                if prereq_ids and not all(prereq_id in approved_subjects for prereq_id in prereq_ids):
                    # No puede haber aprobado esta materia si no tiene prerrequisitos
                    continue
                
                # Determinar estado (80% aprobado, 15% reprobado, 5% cursando)
                rand = random.random()
                
                if rand < 0.80:  # Aprobado
                    status = 'aprobado'
                    grade = round(random.uniform(3.0, 5.0), 1)
                    credits_earned = subject.credits
                    approved_subjects.add(subject.id)
                elif rand < 0.95:  # Reprobado
                    status = 'reprobado'
                    grade = round(random.uniform(0.0, 2.9), 1)
                    credits_earned = 0
                else:  # Cursando
                    status = 'cursando'
                    grade = None
                    credits_earned = 0
                
                # Asignar período académico
                # Distribuir materias en períodos pasados (5 materias por ciclo)
                cycle_index = subject_index // 5
                
                # Calcular año y ciclo
                # Ciclos: 2024-2, 2025-1, 2025-2, etc.
                base_year = 2024
                if cycle_index == 0:
                    year = 2024
                    cycle = 2  # Empezar desde segundo ciclo 2024
                else:
                    # Cada 2 ciclos = 1 año
                    year = base_year + (cycle_index + 1) // 2
                    cycle = ((cycle_index + 1) % 2) + 1
                
                period_code = f"{year}-{cycle}"
                
                history = AcademicHistory(
                    student_id=student.id,
                    subject_id=subject.id,
                    period=period_code,
                    grade=grade,
                    status=status,
                    credits_earned=credits_earned
                )
                self.db.add(history)
                history_count += 1
                subject_index += 1
        
        self.db.flush()
        print(f"  ✅ {history_count} registros de historial académico creados")
    
    def _create_financial_status(self):
        """Crea estados financieros (80% sin deuda, 20% con deuda)"""
        for student in self.students_created:
            rand = random.random()
            
            if rand < 0.80:  # Sin deuda
                has_debt = 'false'
                debt_amount = 0.0
                payment_status = 'al día'
            elif rand < 0.90:  # Deuda pequeña
                has_debt = 'true'
                debt_amount = round(random.uniform(100, 500), 2)
                payment_status = 'pendiente'
            elif rand < 0.97:  # Deuda mediana
                has_debt = 'true'
                debt_amount = round(random.uniform(500, 2000), 2)
                payment_status = 'pendiente'
            else:  # Deuda grande
                has_debt = 'true'
                debt_amount = round(random.uniform(2000, 5000), 2)
                payment_status = 'moroso'
            
            financial_status = FinancialStatus(
                student_id=student.id,
                has_debt=has_debt,
                debt_amount=debt_amount,
                payment_status=payment_status,
                last_updated=date.today()
            )
            self.db.add(financial_status)
        
        self.db.flush()
        print(f"  ✅ {len(self.students_created)} estados financieros creados")
    
    def _count_academic_history(self):
        """Cuenta registros de historial académico"""
        return self.db.query(AcademicHistory).count()


def main(num_students: int = 200):
    """Función principal"""
    db = SessionLocal()
    try:
        simulator = StudentSimulator(db, num_students)
        results = simulator.simulate_all()
        
        print("\n📊 Resumen de datos creados:")
        print(f"  - Estudiantes: {results['students']}")
        print(f"  - Historial académico: {results['academic_history']}")
        print(f"  - Estados financieros: {results['financial_status']}")
        
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
    parser = argparse.ArgumentParser(description='Simular estudiantes')
    parser.add_argument('--num-students', type=int, default=200, help='Número de estudiantes a crear')
    args = parser.parse_args()
    
    main(args.num_students)


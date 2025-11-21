"""
Script para simular datos de Odoo (sistema externo):
- Programas académicos
- Asignaturas (subjects)
- Prerrequisitos
- Malla curricular (study_plans)
- Profesores
- Aulas
- Reglas académicas
"""
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from faker import Faker
import random
from datetime import datetime

from app.database import SessionLocal
from app.models.source.academic import Program, Subject, Prerequisite, StudyPlan
from app.models.source.people import Professor
from app.models.source.infrastructure import Classroom
from app.models.source.rules import AcademicRule
from scripts.parse_programs import ProgramParser

fake = Faker('es_ES')  # Español
Faker.seed(42)  # Para reproducibilidad


class OdooSimulator:
    """Simulador de datos de Odoo"""
    
    def __init__(self, db: Session):
        self.db = db
        self.programs_created = []
        self.subjects_created = []
        self.professors_created = []
        self.classrooms_created = []
    
    def simulate_all(self):
        """Ejecuta toda la simulación de Odoo"""
        print("🚀 Iniciando simulación de datos Odoo...")
        
        # 1. Parsear programas desde markdown
        print("\n📚 Parseando programas desde archivos markdown...")
        parser = ProgramParser(str(backend_dir.parent / "docs"))
        programs_data = parser.parse_all_programs()
        
        if not programs_data:
            raise ValueError("No se encontraron programas para simular")
        
        print(f"✅ {len(programs_data)} programas encontrados")
        
        # 2. Crear programas
        print("\n🏫 Creando programas académicos...")
        self._create_programs(programs_data)
        
        # 3. Crear asignaturas
        print("\n📖 Creando asignaturas...")
        self._create_subjects(programs_data)
        
        # 4. Crear malla curricular
        print("\n📋 Creando malla curricular...")
        self._create_study_plans(programs_data)
        
        # 5. Crear prerrequisitos
        print("\n🔗 Creando prerrequisitos...")
        self._create_prerequisites(programs_data)
        
        # 6. Crear profesores
        print("\n👨‍🏫 Creando profesores...")
        self._create_professors()
        
        # 7. Crear aulas
        print("\n🏢 Creando aulas...")
        self._create_classrooms()
        
        # 8. Crear reglas académicas
        print("\n📜 Creando reglas académicas...")
        self._create_academic_rules()
        
        self.db.commit()
        print("\n✅ Simulación de Odoo completada exitosamente!")
        
        return {
            'programs': len(self.programs_created),
            'subjects': len(self.subjects_created),
            'professors': len(self.professors_created),
            'classrooms': len(self.classrooms_created)
        }
    
    def _create_programs(self, programs_data: list):
        """Crea programas académicos"""
        for prog_data in programs_data:
            program = Program(
                code=prog_data['code'],
                name=prog_data['name'],
                faculty="Facultad de Ciencias Técnicas",
                credits_required=80,  # 20 materias × 4 créditos
                duration_semesters=4
            )
            self.db.add(program)
            self.programs_created.append(program)
        
        self.db.flush()
        print(f"  ✅ {len(self.programs_created)} programas creados")
    
    def _create_subjects(self, programs_data: list):
        """Crea asignaturas para cada programa"""
        program_map = {p.code: p for p in self.programs_created}
        
        for prog_data in programs_data:
            program = program_map[prog_data['code']]
            subject_number = 1
            
            for subj_data in prog_data['subjects']:
                # Generar código de asignatura
                subject_code = f"{program.code}-SUB{subject_number:03d}"
                
                # Determinar distribución de horas
                credits = subj_data['credits']
                hours_per_week = subj_data['hours_per_week']
                
                # Distribuir horas según tipo de materia
                if 'laboratorio' in subj_data['name'].lower() or 'práctica' in subj_data['name'].lower():
                    theory_hours = 0
                    practice_hours = hours_per_week
                    lab_hours = 0
                elif 'teoría' in subj_data['name'].lower():
                    theory_hours = hours_per_week
                    practice_hours = 0
                    lab_hours = 0
                else:
                    # Distribución mixta
                    theory_hours = hours_per_week // 2
                    practice_hours = hours_per_week - theory_hours
                    lab_hours = 0
                
                subject = Subject(
                    code=subject_code,
                    name=subj_data['name'],
                    credits=credits,
                    theory_hours=theory_hours,
                    practice_hours=practice_hours,
                    lab_hours=lab_hours,
                    program_id=program.id
                )
                self.db.add(subject)
                self.subjects_created.append(subject)
                subject_number += 1
        
        self.db.flush()
        print(f"  ✅ {len(self.subjects_created)} asignaturas creadas")
    
    def _create_study_plans(self, programs_data: list):
        """Crea malla curricular (distribuye materias en semestres)"""
        program_map = {p.code: p for p in self.programs_created}
        subject_map = {s.code: s for s in self.subjects_created}
        
        study_plans_created = 0
        
        for prog_data in programs_data:
            program = program_map[prog_data['code']]
            
            # Distribuir 20 materias en 4 semestres (5 por semestre)
            subjects = prog_data['subjects']
            for i, subj_data in enumerate(subjects):
                subject_code = f"{program.code}-SUB{i+1:03d}"
                subject = subject_map[subject_code]
                
                # Asignar semestre (1-4)
                semester = (i // 5) + 1
                
                study_plan = StudyPlan(
                    program_id=program.id,
                    subject_id=subject.id,
                    semester=semester,
                    is_mandatory=True
                )
                self.db.add(study_plan)
                study_plans_created += 1
        
        self.db.flush()
        print(f"  ✅ {study_plans_created} registros de malla curricular creados")
    
    def _create_prerequisites(self, programs_data: list):
        """Crea red de prerrequisitos"""
        program_map = {p.code: p for p in self.programs_created}
        subject_map = {s.code: s for s in self.subjects_created}
        
        prerequisites_created = 0
        
        for prog_data in programs_data:
            program = program_map[prog_data['code']]
            subjects = prog_data['subjects']
            
            # Crear mapa de nombres de materias a códigos
            name_to_subject = {}
            for i, subj_data in enumerate(subjects):
                subject_code = f"{program.code}-SUB{i+1:03d}"
                name_to_subject[subj_data['name']] = subject_map[subject_code]
            
            # Procesar prerrequisitos
            for i, subj_data in enumerate(subjects):
                if not subj_data.get('prerequisites'):
                    continue
                
                subject_code = f"{program.code}-SUB{i+1:03d}"
                subject = subject_map[subject_code]
                
                prereq_name = subj_data['prerequisites']
                
                # Buscar materia prerrequisito por nombre
                prereq_subject = name_to_subject.get(prereq_name)
                
                if prereq_subject:
                    prerequisite = Prerequisite(
                        subject_id=subject.id,
                        prerequisite_subject_id=prereq_subject.id,
                        type='obligatorio'
                    )
                    self.db.add(prerequisite)
                    prerequisites_created += 1
                else:
                    print(f"  ⚠️  No se encontró prerrequisito '{prereq_name}' para {subject.name}")
        
        self.db.flush()
        print(f"  ✅ {prerequisites_created} prerrequisitos creados")
    
    def _create_professors(self):
        """Crea profesores (30+)"""
        departments = [
            "Aviación y Transporte Aéreo",
            "Soldadura y Construcción Marina",
            "Mecánica y Equipo Pesado",
            "Logística y Comercio Internacional",
            "Topografía y Geomática",
            "Matemáticas y Ciencias Básicas",
            "Idiomas",
            "Seguridad Industrial"
        ]
        
        specialties = {
            "Aviación y Transporte Aéreo": [
                "Seguridad Aeronáutica", "Tripulación de Cabina", "Normativa Aérea"
            ],
            "Soldadura y Construcción Marina": [
                "Soldadura Subacuática", "Buceo Profesional", "Estructuras Offshore"
            ],
            "Mecánica y Equipo Pesado": [
                "Motores Diésel", "Sistemas Hidráulicos", "Diagnóstico Electrónico"
            ],
            "Logística y Comercio Internacional": [
                "Comercio Exterior", "Aduanas", "Transporte Multimodal"
            ],
            "Topografía y Geomática": [
                "Levantamientos Topográficos", "GPS y GNSS", "Sistemas de Información Geográfica"
            ],
            "Matemáticas y Ciencias Básicas": [
                "Matemáticas Aplicadas", "Física", "Geometría"
            ],
            "Idiomas": [
                "Inglés Comercial", "Inglés Aeronáutico", "Comunicación"
            ],
            "Seguridad Industrial": [
                "Seguridad Ocupacional", "Normativa Técnica", "Prevención de Riesgos"
            ]
        }
        
        professor_number = 1
        
        for _ in range(35):  # 35 profesores
            department = random.choice(departments)
            specialty_list = specialties.get(department, ["General"])
            specialty = random.choice(specialty_list)
            
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@universidad.edu"
            
            # Asegurar email único
            existing_emails = {p.email for p in self.professors_created}
            counter = 1
            while email in existing_emails:
                email = f"{first_name.lower()}.{last_name.lower()}{counter}@universidad.edu"
                counter += 1
            
            professor = Professor(
                code=f"PROF{professor_number:03d}",
                first_name=first_name,
                last_name=last_name,
                email=email,
                department=department,
                specialty=specialty
            )
            self.db.add(professor)
            self.professors_created.append(professor)
            professor_number += 1
        
        self.db.flush()
        print(f"  ✅ {len(self.professors_created)} profesores creados")
    
    def _create_classrooms(self):
        """Crea aulas (20+)"""
        buildings = ["Edificio A", "Edificio B", "Edificio C", "Edificio D"]
        classroom_types = {
            'aula': {'capacity_range': (30, 50), 'prefix': 'AULA'},
            'laboratorio': {'capacity_range': (20, 30), 'prefix': 'LAB'},
            'auditorio': {'capacity_range': (100, 200), 'prefix': 'AUD'}
        }
        
        classroom_number = 1
        
        # Crear aulas normales
        for _ in range(15):
            building = random.choice(buildings)
            floor = random.randint(1, 4)
            capacity = random.randint(30, 50)
            
            classroom = Classroom(
                code=f"AULA{classroom_number:03d}",
                building=building,
                floor=floor,
                capacity=capacity,
                type='aula'
            )
            self.db.add(classroom)
            self.classrooms_created.append(classroom)
            classroom_number += 1
        
        # Crear laboratorios
        for _ in range(5):
            building = random.choice(buildings)
            floor = random.randint(1, 3)
            capacity = random.randint(20, 30)
            
            classroom = Classroom(
                code=f"LAB{classroom_number:03d}",
                building=building,
                floor=floor,
                capacity=capacity,
                type='laboratorio'
            )
            self.db.add(classroom)
            self.classrooms_created.append(classroom)
            classroom_number += 1
        
        # Crear auditorios
        for _ in range(3):
            building = random.choice(buildings)
            floor = 1  # Auditorios generalmente en primer piso
            capacity = random.randint(100, 200)
            
            classroom = Classroom(
                code=f"AUD{classroom_number:03d}",
                building=building,
                floor=floor,
                capacity=capacity,
                type='auditorio'
            )
            self.db.add(classroom)
            self.classrooms_created.append(classroom)
            classroom_number += 1
        
        self.db.flush()
        print(f"  ✅ {len(self.classrooms_created)} aulas creadas")
    
    def _create_academic_rules(self):
        """Crea reglas académicas"""
        rules = [
            {
                'rule_type': 'max_credits_per_semester',
                'rule_value': '20',
                'description': 'Máximo de créditos permitidos por semestre'
            },
            {
                'rule_type': 'min_credits_to_enroll',
                'rule_value': '8',
                'description': 'Mínimo de créditos requeridos para matricularse'
            },
            {
                'rule_type': 'max_credits_per_cycle',
                'rule_value': '20',
                'description': 'Máximo de créditos permitidos por ciclo académico'
            },
            {
                'rule_type': 'min_grade_to_pass',
                'rule_value': '3.0',
                'description': 'Calificación mínima para aprobar una asignatura'
            }
        ]
        
        for rule_data in rules:
            rule = AcademicRule(
                rule_type=rule_data['rule_type'],
                rule_value=rule_data['rule_value'],
                description=rule_data['description']
            )
            self.db.add(rule)
        
        self.db.flush()
        print(f"  ✅ {len(rules)} reglas académicas creadas")


def main():
    """Función principal"""
    db = SessionLocal()
    try:
        simulator = OdooSimulator(db)
        results = simulator.simulate_all()
        
        print("\n📊 Resumen de datos creados:")
        print(f"  - Programas: {results['programs']}")
        print(f"  - Asignaturas: {results['subjects']}")
        print(f"  - Profesores: {results['professors']}")
        print(f"  - Aulas: {results['classrooms']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


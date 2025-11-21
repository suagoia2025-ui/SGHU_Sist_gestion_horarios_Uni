# Plan de Trabajo - SGHU (Sistema de Gestión de Horarios Universitarios)

## 📊 Resumen del Proyecto

**Propósito:** Sistema para gestionar la matrícula y generación automática de horarios en una universidad, con simulación de integraciones con Odoo (ERP) y Moodle (LMS).

**Stack Tecnológico:**
- Backend: FastAPI (Python 3.11+)
- Base de datos: PostgreSQL 15+
- Workers: Celery + Redis
- Motor de horarios: Google OR-Tools CP-SAT + Algoritmos Genéticos (DEAP)
- Frontend (futuro): Vue 3 + TypeScript

**Duración estimada:** 31 días (aproximadamente 6-7 semanas)

---

## 📋 FASE 0: Setup del Proyecto
**Duración:** Día 1  
**Objetivo:** Configurar el entorno de desarrollo completo

### Tareas
1. [ ] Crear estructura de carpetas del proyecto
2. [ ] Configurar Git + GitHub con .gitignore apropiado
3. [ ] Crear entorno virtual Python (`python -m venv venv`)
4. [ ] Instalar dependencias base:
   - FastAPI
   - uvicorn
   - SQLAlchemy
   - psycopg2-binary
   - alembic
   - pydantic-settings
5. [ ] Configurar Docker Compose (PostgreSQL + Redis)
6. [ ] Crear archivo de configuración (.env.example)
7. [ ] Documentar setup en README.md

### Estructura de carpetas propuesta
```
sghu/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   ├── repositories/
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   └── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       └── __init__.py
│   │   └── core/
│   │       └── __init__.py
│   ├── tests/
│   │   └── __init__.py
│   ├── scripts/
│   ├── alembic/
│   ├── logs/
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   └── docker-compose.yml
├── docs/
│   └── plan-trabajo.md
└── README.md
```

### Deliverables
- [ ] Repositorio Git inicializado
- [ ] Entorno virtual configurado
- [ ] Docker Compose funcionando (PostgreSQL accesible)
- [ ] README.md con instrucciones de setup

---

## 📋 FASE 1: Diseño de Base de Datos
**Duración:** Días 2-3  
**Objetivo:** Diseñar y crear esquemas completos de base de datos

### 1.1 Esquema "source" (Datos simulados de sistemas externos)

#### Tablas Odoo - Datos Institucionales
- [ ] **programs**: Programas académicos (Ingeniería, Medicina, etc.)
  - `id, code, name, faculty, credits_required, duration_semesters`
- [ ] **subjects**: Catálogo de asignaturas
  - `id, code, name, credits, theory_hours, practice_hours, lab_hours, program_id`
- [ ] **prerequisites**: Red de prerrequisitos
  - `id, subject_id, prerequisite_subject_id, type (obligatorio/correquisito)`
- [ ] **study_plans**: Malla curricular
  - `id, program_id, subject_id, semester, is_mandatory`
- [ ] **professors**: Docentes
  - `id, code, first_name, last_name, email, department, specialty`
- [ ] **classrooms**: Aulas
  - `id, code, building, floor, capacity, type (laboratorio/aula/auditorio)`
- [ ] **academic_rules**: Reglas institucionales
  - `id, rule_type, rule_value, description`

#### Tablas Estudiantes
- [ ] **students**: Datos personales
  - `id, code, first_name, last_name, email, program_id, current_semester, admission_date`
- [ ] **academic_history**: Historial académico
  - `id, student_id, subject_id, period, grade, status (aprobado/reprobado/cursando), credits_earned`
- [ ] **financial_status**: Estado financiero
  - `id, student_id, has_debt, debt_amount, payment_status, last_updated`

#### Tablas Oferta Académica
- [ ] **academic_periods**: Períodos académicos
  - `id, code, name, start_date, end_date, enrollment_start, enrollment_end, status`
- [ ] **course_sections**: Secciones ofertadas
  - `id, period_id, subject_id, section_number, professor_id, capacity, enrolled_count, classroom_id`
- [ ] **section_schedules**: Horarios de secciones
  - `id, section_id, day_of_week, start_time, end_time, session_type (teoría/práctica/laboratorio)`

#### Tablas Moodle - Simulación LMS
- [ ] **moodle_courses**: Cursos en Moodle
  - `id, course_code, course_name, section_id, moodle_id, created_at`
- [ ] **moodle_enrollments**: Inscripciones
  - `id, moodle_course_id, student_id, role, enrollment_date`

### 1.2 Esquema "sghu" (Resultados del sistema)

#### Tablas de Matrícula
- [ ] **enrollment_periods**: Control de períodos
  - `id, academic_period_id, status, opened_at, closed_at`
- [ ] **student_enrollments**: Matrículas
  - `id, enrollment_period_id, student_id, total_credits, status, created_at, confirmed_at`
- [ ] **enrollment_subjects**: Asignaturas por matrícula
  - `id, enrollment_id, section_id, status (pendiente/confirmado/rechazado)`

#### Tablas de Horarios
- [ ] **generated_schedules**: Horarios generados
  - `id, enrollment_id, generation_method (constraint_solver/genetic), quality_score, processing_time, status, created_at`
- [ ] **schedule_slots**: Bloques de horario
  - `id, schedule_id, section_id, day_of_week, start_time, end_time`
- [ ] **schedule_conflicts**: Conflictos detectados
  - `id, schedule_id, conflict_type, description, severity, resolved`

#### Tablas de Sistema
- [ ] **processing_logs**: Logs de ejecución
  - `id, enrollment_id, process_type, status, message, started_at, finished_at, error_details`

### 1.3 Deliverables Fase 1
- [ ] Diagrama ER completo (usar draw.io, dbdiagram.io o similar)
- [ ] Scripts SQL de creación (DDL) para ambos esquemas
- [ ] Documentación detallada de cada tabla:
  - Propósito de la tabla
  - Descripción de columnas
  - Índices necesarios
  - Constraints y relaciones
- [ ] Script de inicialización de BD (`scripts/init_db.sql`)

### Recursos de aprendizaje
- PostgreSQL Schemas: https://www.postgresql.org/docs/current/ddl-schemas.html
- Database Design Best Practices
- Foreign Keys y Constraints

---

## 📋 FASE 2: Scripts de Simulación
**Duración:** Días 4-6  
**Objetivo:** Crear scripts Python para poblar la BD con datos realistas

### 2.1 Script Simulador de Odoo
**Archivo:** `scripts/simulate_odoo.py`

- [ ] Generar 5 programas académicos
  - Técnico Superior en Logística Internacional, Técnico Superior en Mecánica de Equipo Pesado, Técnico Superior en Soldadura Subacuática, Técnico Superior en Asistencia de Tripulación Aérea y Técnico Superior en Topografía.
- [ ] Generar 100+ asignaturas coherentes
  - Distribuidas por programa
  - Con créditos realistas (1-4 créditos)
  - Nombres coherentes por área
- [ ] Crear red de prerrequisitos lógica
  - Asignaturas básicas → intermedias → avanzadas
  - Respetar secuencialidad (Cálculo I → Cálculo II)
- [ ] Generar 30+ profesores
  - Distribuidos por departamentos
  - Con especialidades coherentes
- [ ] Crear 20+ aulas
  - Diferentes capacidades (20-200 personas)
  - Tipos variados (aulas, laboratorios, auditorios)
- [ ] Configurar reglas académicas
  - Límite de créditos por semestre (12-20)
  - Mínimo de créditos para inscribirse (6)

### 2.2 Script Simulador de Estudiantes
**Archivo:** `scripts/simulate_students.py`

- [ ] Generar 200+ estudiantes
  - Distribuidos en diferentes programas
  - En diferentes semestres (1-10)
  - Nombres realistas (usar biblioteca Faker)
- [ ] Crear historial académico coherente
  - Materias aprobadas según semestre actual
  - Respetando prerrequisitos
  - Calificaciones variadas (2.0-5.0)
  - Algunos estudiantes con materias reprobadas
- [ ] Simular estados financieros
  - 80% sin deudas
  - 20% con deudas variadas
  - Diferentes estados de pago

### 2.3 Script Simulador de Oferta Académica
**Archivo:** `scripts/simulate_offer.py`

- [ ] Crear período académico activo (ej: 2025-1)
- [ ] Generar secciones para cada asignatura
  - 1-3 secciones por asignatura popular
  - Horarios realistas (7am-9pm)
  - Sin choques de profesores
  - Sin choques de aulas
- [ ] Asignar capacidades según tipo de aula
- [ ] Crear horarios distribuidos en la semana
  - Sesiones de 2 o 3 horas
  - Lunes a sábado
  - Bloques coherentes (teoría + práctica)

### 2.4 Script Maestro
**Archivo:** `scripts/populate_db.py`
```python
"""
Script maestro que ejecuta todos los simuladores en orden correcto
"""
def main():
    # 1. Limpiar BD (opcional)
    # 2. Simular datos Odoo
    # 3. Simular estudiantes
    # 4. Simular oferta académica
    # 5. Validar integridad
    # 6. Mostrar resumen de datos generados
```

- [ ] Implementar función de limpieza de BD
- [ ] Ejecutar simuladores en orden correcto
- [ ] Parámetros configurables:
  - Cantidad de estudiantes
  - Cantidad de asignaturas
  - Cantidad de secciones
- [ ] Validar integridad referencial
- [ ] Logging detallado del proceso
- [ ] Generar reporte de datos creados

### 2.5 Deliverables Fase 2
- [ ] Scripts Python funcionales y documentados
- [ ] Base de datos poblada con datos realistas
- [ ] Script de limpieza/reset: `scripts/reset_db.py`
- [ ] Documentación de datos generados:
  - Estadísticas (cantidad de registros)
  - Ejemplos de datos
  - Casos especiales creados
- [ ] README con instrucciones de uso de scripts

### Recursos de aprendizaje
- Biblioteca Faker para datos realistas
- SQLAlchemy Core para inserción masiva
- Psycopg2 para conexión PostgreSQL
- Logging en Python

---

## 📋 FASE 3: Estructura FastAPI Base
**Duración:** Días 7-9  
**Objetivo:** Implementar arquitectura base del backend con FastAPI

### 3.1 Configuración del Proyecto

**Estructura de carpetas detallada:**
```
backend/app/
├── __init__.py
├── main.py                 # Entry point, app initialization
├── config.py               # Settings usando pydantic-settings
├── database.py             # Database connection, sessions
│
├── models/                 # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── source/            # Modelos esquema "source"
│   │   ├── academic.py    # Programs, Subjects, Prerequisites
│   │   ├── people.py      # Students, Professors
│   │   ├── infrastructure.py  # Classrooms
│   │   └── offer.py       # AcademicPeriods, CourseSections
│   └── sghu/              # Modelos esquema "sghu"
│       ├── enrollment.py  # Enrollments, EnrollmentSubjects
│       └── schedule.py    # Schedules, ScheduleSlots
│
├── schemas/               # Pydantic schemas (DTOs)
│   ├── __init__.py
│   ├── student.py
│   ├── subject.py
│   ├── enrollment.py
│   └── schedule.py
│
├── repositories/          # Data access layer
│   ├── __init__.py
│   ├── base.py           # Base repository class
│   ├── student_repository.py
│   ├── subject_repository.py
│   └── enrollment_repository.py
│
├── services/             # Business logic layer
│   ├── __init__.py
│   ├── student_service.py
│   ├── enrollment_service.py
│   └── validation_service.py
│
├── api/                  # API endpoints
│   ├── __init__.py
│   ├── deps.py          # Dependencies (get_db, auth, etc.)
│   └── v1/
│       ├── __init__.py
│       ├── students.py
│       ├── subjects.py
│       ├── enrollment.py
│       └── schedules.py
│
└── core/                # Core utilities
    ├── __init__.py
    ├── exceptions.py    # Custom exceptions
    ├── logging.py       # Logging configuration
    └── utils.py         # Helper functions
```

### 3.2 Archivos Base a Implementar

#### Config (config.py)
- [ ] Configuración usando pydantic-settings
- [ ] Variables de entorno (.env):
  - DATABASE_URL
  - SECRET_KEY
  - LOG_LEVEL
  - CORS_ORIGINS

#### Database (database.py)
- [ ] Engine de SQLAlchemy
- [ ] SessionLocal factory
- [ ] Base declarativa
- [ ] Dependency para obtener sesión DB

#### Main (main.py)
- [ ] Inicialización de FastAPI app
- [ ] Configuración de CORS
- [ ] Inclusión de routers
- [ ] Middleware de logging
- [ ] Health check endpoint

### 3.3 Models SQLAlchemy

- [ ] Implementar modelos para esquema "source":
  - Program
  - Subject
  - Prerequisite
  - Student
  - AcademicHistory
  - Professor
  - Classroom
  - AcademicPeriod
  - CourseSection
  - SectionSchedule

- [ ] Implementar modelos para esquema "sghu":
  - EnrollmentPeriod
  - StudentEnrollment
  - EnrollmentSubject
  - GeneratedSchedule
  - ScheduleSlot
  - ScheduleConflict

### 3.4 Schemas Pydantic

- [ ] StudentBase, StudentCreate, StudentRead
- [ ] SubjectBase, SubjectRead
- [ ] CourseSectionRead (con relaciones)
- [ ] EnrollmentCreate, EnrollmentRead
- [ ] ScheduleRead

### 3.5 Repositories (Capa de Datos)
```python
# Ejemplo: repositories/base.py
class BaseRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, id: int):
        pass
    
    def get_all(self, skip: int = 0, limit: int = 100):
        pass
    
    def create(self, obj):
        pass
```

- [ ] StudentRepository
- [ ] SubjectRepository
- [ ] CourseSectionRepository
- [ ] EnrollmentRepository

### 3.6 Services (Lógica de Negocio)

- [ ] StudentService: operaciones sobre estudiantes
- [ ] SubjectService: catálogo y oferta
- [ ] EnrollmentService: proceso de matrícula (básico)

### 3.7 API Endpoints (v1)

#### Endpoints de consulta (READ):
- [ ] `GET /api/v1/students/{student_id}` - Obtener estudiante
- [ ] `GET /api/v1/students/{student_id}/academic-history` - Historial
- [ ] `GET /api/v1/subjects` - Listar asignaturas (con filtros)
- [ ] `GET /api/v1/subjects/{subject_id}` - Detalle asignatura
- [ ] `GET /api/v1/academic-periods/current` - Período activo
- [ ] `GET /api/v1/course-sections` - Oferta académica (filtros por periodo/programa)
- [ ] `GET /api/v1/course-sections/{section_id}` - Detalle sección

#### Health check:
- [ ] `GET /health` - Estado del servidor
- [ ] `GET /api/v1/health/db` - Estado de BD

### 3.8 Deliverables Fase 3
- [ ] FastAPI corriendo en `http://localhost:8000`
- [ ] Documentación Swagger en `/docs`
- [ ] Todos los endpoints básicos funcionando
- [ ] Respuestas con formato JSON correcto
- [ ] Manejo básico de errores (404, 500)
- [ ] Logs del servidor configurados
- [ ] Archivo `requirements.txt` actualizado
- [ ] README con instrucciones para correr el servidor

### Testing básico
- [ ] Probar endpoints con Thunder Client / Postman
- [ ] Verificar respuestas para datos existentes
- [ ] Verificar manejo de IDs inexistentes

### Recursos de aprendizaje
- FastAPI Tutorial: https://fastapi.tiangolo.com/tutorial/
- SQLAlchemy 2.0 ORM: https://docs.sqlalchemy.org/
- Pydantic V2: https://docs.pydantic.dev/
- Repository Pattern
- Dependency Injection en FastAPI

---

## 📋 FASE 4: Lógica de Validación
**Duración:** Días 10-12  
**Objetivo:** Implementar todas las validaciones de reglas de negocio para matrícula

### 4.1 Service de Validación

**Archivo:** `app/services/validation_service.py`

#### Validaciones a implementar:

##### 1. Validación de Estado Financiero
- [ ] Verificar si estudiante tiene deudas
- [ ] Bloquear matrícula si `has_debt = True`
- [ ] Retornar monto de deuda
```python
def validate_financial_status(student_id: int) -> ValidationResult:
    """
    Verifica estado financiero del estudiante.
    Retorna: is_valid, message, debt_amount
    """
    pass
```

##### 2. Validación de Prerrequisitos
- [ ] Obtener prerrequisitos de cada asignatura
- [ ] Verificar en historial académico si están aprobados
- [ ] Manejar correquisitos (pueden cursarse simultáneamente)
- [ ] Retornar prerrequisitos faltantes
```python
def validate_prerequisites(student_id: int, subject_id: int) -> ValidationResult:
    """
    Verifica si el estudiante cumple prerrequisitos.
    Retorna: is_valid, missing_prerequisites[]
    """
    pass
```

##### 3. Validación de Límite de Créditos
- [ ] Obtener límite de créditos del programa/reglas
- [ ] Sumar créditos de asignaturas seleccionadas
- [ ] Verificar que no exceda máximo
- [ ] Verificar que cumpla mínimo
```python
def validate_credit_limit(student_id: int, selected_subjects: List[int]) -> ValidationResult:
    """
    Verifica límite de créditos.
    Retorna: is_valid, total_credits, max_allowed, min_required
    """
    pass
```

##### 4. Validación de Cupos Disponibles
- [ ] Verificar cupos de cada sección
- [ ] Considerar reservas (si aplica)
- [ ] Retornar disponibilidad actual
```python
def validate_section_capacity(section_id: int) -> ValidationResult:
    """
    Verifica cupos disponibles en sección.
    Retorna: is_valid, capacity, enrolled_count, available
    """
    pass
```

##### 5. Validación de Choques de Horario
- [ ] Obtener horarios de secciones seleccionadas
- [ ] Detectar solapamientos de tiempo
- [ ] Considerar día de la semana
- [ ] Retornar choques detectados
```python
def validate_schedule_conflicts(section_ids: List[int]) -> ValidationResult:
    """
    Detecta choques de horario entre secciones.
    Retorna: is_valid, conflicts[]
    """
    pass
```

##### 6. Validación de Matrícula Repetida
- [ ] Verificar que no esté matriculada la misma asignatura
- [ ] Permitir repetir solo si fue reprobada
- [ ] Límite de veces que puede repetir (si aplica)
```python
def validate_duplicate_enrollment(student_id: int, subject_id: int) -> ValidationResult:
    """
    Verifica si ya está matriculado o ya aprobó la materia.
    Retorna: is_valid, status (nuevo/repeticion/ya_aprobado)
    """
    pass
```

### 4.2 Service de Matrícula

**Archivo:** `app/services/enrollment_service.py`

- [ ] Orquestar todas las validaciones
- [ ] Método: `validate_enrollment_request()`
- [ ] Retornar resultado consolidado:
  - Lista de validaciones pasadas
  - Lista de validaciones fallidas
  - Puede proceder: sí/no
```python
class EnrollmentService:
    def __init__(self, db: Session):
        self.db = db
        self.validation_service = ValidationService(db)
    
    def validate_enrollment_request(
        self, 
        student_id: int, 
        section_ids: List[int]
    ) -> EnrollmentValidationResult:
        """
        Ejecuta todas las validaciones necesarias.
        Retorna resultado consolidado.
        """
        results = []
        
        # 1. Validar estado financiero
        # 2. Para cada sección, validar:
        #    - Prerrequisitos
        #    - Cupos
        # 3. Validar créditos totales
        # 4. Validar choques
        
        return EnrollmentValidationResult(
            is_valid=all(r.is_valid for r in results),
            validations=results,
            can_proceed=...,
            error_summary=...
        )
```

### 4.3 Nuevos Schemas Pydantic

**Archivo:** `app/schemas/validation.py`

- [ ] `ValidationResult`: resultado individual de validación
- [ ] `EnrollmentValidationResult`: resultado consolidado
- [ ] `EnrollmentRequest`: petición de matrícula
- [ ] `EligibleSubjectsResponse`: materias disponibles
```python
class ValidationResult(BaseModel):
    validation_type: str
    is_valid: bool
    message: str
    details: Optional[Dict] = None

class EnrollmentRequest(BaseModel):
    student_id: int
    academic_period_id: int
    section_ids: List[int]

class EnrollmentValidationResult(BaseModel):
    is_valid: bool
    can_proceed: bool
    validations: List[ValidationResult]
    error_summary: Optional[str]
```

### 4.4 Nuevos Endpoints

**Archivo:** `app/api/v1/enrollment.py`

#### 1. Validar selección de materias
```python
@router.post("/api/v1/enrollment/validate")
def validate_enrollment(
    request: EnrollmentRequest,
    db: Session = Depends(get_db)
) -> EnrollmentValidationResult:
    """
    Valida una solicitud de matrícula sin persistirla.
    Retorna todas las validaciones ejecutadas.
    """
    pass
```

#### 2. Obtener materias elegibles
```python
@router.get("/api/v1/students/{student_id}/eligible-subjects")
def get_eligible_subjects(
    student_id: int,
    academic_period_id: int,
    db: Session = Depends(get_db)
) -> List[SubjectEligibilityInfo]:
    """
    Retorna asignaturas que el estudiante puede cursar.
    Incluye info de prerrequisitos cumplidos/faltantes.
    """
    pass
```

#### 3. Verificar estado de matrícula
```python
@router.get("/api/v1/students/{student_id}/enrollment-status")
def get_enrollment_status(
    student_id: int,
    db: Session = Depends(get_db)
) -> EnrollmentStatusResponse:
    """
    Estado actual: puede matricularse, razones de bloqueo, etc.
    """
    pass
```

### 4.5 Tests Unitarios

**Archivo:** `tests/test_validation_service.py`

- [ ] Test: Estudiante con deuda no puede matricularse
- [ ] Test: Prerrequisitos faltantes
- [ ] Test: Exceder límite de créditos
- [ ] Test: Sección sin cupos
- [ ] Test: Choques de horario
- [ ] Test: Matrícula repetida (permitida si reprobó)
- [ ] Test: Validación exitosa (todos los checks pasan)

**Archivo:** `tests/test_enrollment_endpoints.py`

- [ ] Test: POST /enrollment/validate con datos válidos
- [ ] Test: POST /enrollment/validate con datos inválidos
- [ ] Test: GET /eligible-subjects retorna lista correcta
- [ ] Test: Estudiante bloqueado financieramente

### 4.6 Deliverables Fase 4
- [ ] `ValidationService` implementado y funcionando
- [ ] `EnrollmentService` con validación completa
- [ ] Endpoints de validación funcionando
- [ ] Tests unitarios pasando (coverage > 80% en validaciones)
- [ ] Documentación de reglas de negocio:
  - Tabla con todas las validaciones
  - Códigos de error
  - Mensajes de usuario
- [ ] Postman collection con casos de prueba

### Documentación requerida

**Crear:** `docs/reglas-negocio.md`

Tabla de validaciones:
| Validación        | Tipo    | Bloqueo | Mensaje Usuario                             |
|-------------------|---------|---------|---------------------------------------------|
| Estado financiero | Crítico | Sí      | "Tienes una deuda pendiente de $X"          |
| Prerrequisitos    | Crítico | Sí      | "Debes aprobar [materias] primero"          |
| Límite créditos   | Crítico | Sí      | "Máximo permitido: X créditos"              |
| Cupos | Crítico   | Sí      | "No hay cupos disponibles"                            |
| Choques horario   | Crítico | Sí      | "Conflicto entre [sección A] y [sección B]" |

### Recursos de aprendizaje
- Business Logic Layer patterns
- Domain Driven Design (DDD) basics
- Pytest para Python
- Exception handling best practices

---

## 📋 FASE 5: Motor de Horarios - Parte 1 (Restricciones Duras)
**Duración:** Días 13-17  
**Objetivo:** Implementar solver básico con OR-Tools que genere horarios viables

### 5.1 Investigación y Setup

#### Día 13: Estudio de OR-Tools
- [ ] Leer documentación oficial de CP-SAT
- [ ] Estudiar ejemplos de scheduling:
  - Job Shop Scheduling
  - Nurse Scheduling
  - Course Timetabling
- [ ] Entender conceptos clave:
  - Variables de decisión
  - Restricciones (constraints)
  - Dominio de variables
  - Solver y búsqueda

#### Recursos específicos:
- Google OR-Tools CP-SAT: https://developers.google.com/optimization/cp
- Ejemplo de Timetabling: https://developers.google.com/optimization/scheduling
- Paper: "Constraint Programming for Timetabling"

#### Instalación:
```bash
pip install ortools
```

#### Prueba básica:
```python
from ortools.sat.python import cp_model

# Crear modelo simple
model = cp_model.CpModel()
x = model.NewIntVar(0, 10, 'x')
y = model.NewIntVar(0, 10, 'y')
model.Add(x + y == 10)

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    print(f'x = {solver.Value(x)}')
    print(f'y = {solver.Value(y)}')
```

### 5.2 Modelado del Problema

#### Día 14: Definir variables y dominio

**Archivo:** `app/services/schedule_engine/models.py`

##### Variables de decisión:
```python
"""
Para cada estudiante-sección-timeslot:
    x[student_id, section_id, timeslot_id] = 1 si asignado, 0 si no

Timeslot: combinación de día + bloque horario
    Ejemplo: (Lunes, 7am-9am), (Lunes, 9am-11am), ...
"""
```

- [ ] Definir estructura de Timeslot
- [ ] Crear mapa de secciones disponibles
- [ ] Identificar variables de decisión

**Estructuras de datos:**
```python
@dataclass
class TimeSlot:
    id: int
    day_of_week: int  # 0=Lunes, 6=Domingo
    start_time: time
    end_time: time
    
    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """Detecta solapamiento de horarios"""
        pass

@dataclass
class Section:
    id: int
    subject_id: int
    professor_id: int
    classroom_id: int
    capacity: int
    enrolled_count: int
    timeslots: List[TimeSlot]

@dataclass
class Student:
    id: int
    program_id: int
    approved_subjects: List[int]
    selected_sections: List[int]  # Secciones que quiere cursar
```

### 5.3 Implementar Restricciones Duras

#### Día 15-16: Constraint Solver

**Archivo:** `app/services/schedule_engine/constraint_solver.py`
```python
class ConstraintScheduleSolver:
    """
    Genera horarios usando CP-SAT resolviendo solo restricciones duras.
    """
    
    def __init__(self, student: Student, available_sections: List[Section]):
        self.student = student
        self.sections = available_sections
        self.model = cp_model.CpModel()
        self.variables = {}
    
    def create_variables(self):
        """Crear variables de decisión"""
        pass
    
    def add_constraints(self):
        """Agregar todas las restricciones duras"""
        self._add_capacity_constraints()
        self._add_time_conflict_constraints()
        self._add_professor_conflict_constraints()
        self._add_classroom_conflict_constraints()
        self._add_prerequisite_constraints()
        self._add_one_section_per_subject_constraint()
    
    def solve(self) -> ScheduleSolution:
        """Ejecutar solver y retornar solución"""
        pass
```

##### Restricciones a implementar:

**1. Sin choques de horario para el estudiante**
```python
def _add_time_conflict_constraints(self):
    """
    Un estudiante no puede estar en dos lugares al mismo tiempo.
    Si sección A y B tienen timeslots que se solapan,
    no pueden estar ambas asignadas.
    """
    for section_a in self.sections:
        for section_b in self.sections:
            if section_a.id >= section_b.id:
                continue
            
            if self._have_time_overlap(section_a, section_b):
                # No pueden estar ambas asignadas
                self.model.Add(
                    self.variables[(section_a.id)] + 
                    self.variables[(section_b.id)] <= 1
                )
```

**2. Respetar cupos de sección**
```python
def _add_capacity_constraints(self):
    """
    Una sección no puede exceder su capacidad.
    (Esta restricción es más relevante cuando procesamos múltiples estudiantes)
    """
    for section in self.sections:
        if section.enrolled_count >= section.capacity:
            # Forzar que esta sección NO sea seleccionada
            self.model.Add(self.variables[section.id] == 0)
```

**3. Sin choques de profesor**
```python
def _add_professor_conflict_constraints(self):
    """
    Un profesor no puede dar dos clases simultáneas.
    (Relevante si generamos horarios para múltiples estudiantes)
    """
    pass
```

**4. Sin choques de aula**
```python
def _add_classroom_conflict_constraints(self):
    """
    Un aula no puede estar ocupada por dos secciones al mismo tiempo.
    """
    pass
```

**5. Una sola sección por asignatura**
```python
def _add_one_section_per_subject_constraint(self):
    """
    El estudiante debe cursar exactamente UNA sección de cada asignatura seleccionada.
    """
    # Agrupar secciones por asignatura
    sections_by_subject = {}
    for section in self.sections:
        if section.subject_id not in sections_by_subject:
            sections_by_subject[section.subject_id] = []
        sections_by_subject[section.subject_id].append(section)
    
    # Para cada asignatura, suma de variables debe ser 1
    for subject_id, sections in sections_by_subject.items():
        self.model.Add(
            sum(self.variables[s.id] for s in sections) == 1
        )
```

**6. Prerrequisitos cumplidos**
```python
def _add_prerequisite_constraints(self):
    """
    Solo permitir seleccionar secciones de asignaturas 
    cuyos prerrequisitos estén aprobados.
    """
    for section in self.sections:
        subject = get_subject(section.subject_id)
        prerequisites = get_prerequisites(subject.id)
        
        for prereq in prerequisites:
            if prereq.id not in self.student.approved_subjects:
                # Forzar que esta sección NO sea seleccionada
                self.model.Add(self.variables[section.id] == 0)
```

### 5.4 Generar Solución

#### Día 17: Integración y pruebas

**Resultado de solver:**
```python
@dataclass
class ScheduleSolution:
    student_id: int
    is_feasible: bool
    assigned_sections: List[int]
    processing_time: float
    conflicts: List[str]  # Si no es viable, listar conflictos
    
    def to_schedule_slots(self) -> List[ScheduleSlot]:
        """Convertir a slots de horario para BD"""
        pass
```

**Service de generación:**

**Archivo:** `app/services/schedule_service.py`
```python
class ScheduleService:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_schedule_for_student(
        self, 
        student_id: int, 
        selected_subject_ids: List[int]
    ) -> ScheduleSolution:
        """
        Genera horario para un estudiante dado.
        
        Pasos:
        1. Obtener datos del estudiante (historial, aprobados)
        2. Obtener secciones disponibles de las materias seleccionadas
        3. Ejecutar ConstraintScheduleSolver
        4. Si exitoso, persistir en BD (esquema sghu)
        5. Retornar solución
        """
        # Cargar datos
        student = self._load_student_data(student_id)
        sections = self._load_available_sections(selected_subject_ids)
        
        # Resolver
        solver = ConstraintScheduleSolver(student, sections)
        solver.create_variables()
        solver.add_constraints()
        solution = solver.solve()
        
        # Persistir si es viable
        if solution.is_feasible:
            self._save_schedule(solution)
        
        return solution
```

### 5.5 Endpoint de Generación (v1)

**Archivo:** `app/api/v1/schedules.py`
```python
@router.post("/api/v1/schedules/generate")
def generate_schedule(
    request: ScheduleGenerationRequest,
    db: Session = Depends(get_db)
) -> ScheduleSolution:
    """
    Genera horario para estudiante usando solo restricciones duras.
    
    Body:
    {
        "student_id": 123,
        "selected_subject_ids": [1, 2, 3, 4, 5]
    }
    """
    service = ScheduleService(db)
    solution = service.generate_schedule_for_student(
        request.student_id,
        request.selected_subject_ids
    )
    return solution
```

### 5.6 Tests

**Archivo:** `tests/test_constraint_solver.py`

- [ ] Test: Generar horario simple (3 materias, sin conflictos)
- [ ] Test: Detectar choque de horario (2 secciones al mismo tiempo)
- [ ] Test: Sección sin cupos
- [ ] Test: Prerrequisito no cumplido
- [ ] Test: Solución infactible (todas las secciones chocan)
- [ ] Test: Una sola sección por materia

**Casos de prueba manuales:**
- [ ] Estudiante de semestre 1 con 5 materias básicas
- [ ] Estudiante de semestre 5 con materias avanzadas
- [ ] Estudiante con restricciones severas (pocas secciones disponibles)

### 5.7 Deliverables Fase 5
- [ ] `ConstraintScheduleSolver` implementado y funcionando
- [ ] Genera horario 100% viable (sin conflictos)
- [ ] `ScheduleService` con integración completa
- [ ] Endpoint `/schedules/generate` funcionando
- [ ] Tests unitarios pasando
- [ ] Documentación técnica:
  - Explicación del modelado
  - Variables de decisión
  - Restricciones implementadas
  - Ejemplo de entrada/salida
- [ ] Métricas básicas:
  - Tiempo de generación promedio
  - Tasa de éxito (% soluciones factibles)

### Métricas a medir:
```python
# Ejemplo de métricas
{
    "total_requests": 50,
    "successful": 45,
    "failed": 5,
    "avg_processing_time": 1.2,  # segundos
    "max_processing_time": 3.5,
    "min_processing_time": 0.3
}
```

### Recursos de aprendizaje
- Google OR-Tools CP-SAT Solver
- Constraint Programming fundamentals
- Scheduling problems modeling
- Time complexity analysis

**Punto de control:** Al finalizar esta fase debes tener un motor que genere horarios 100% viables, aunque no optimizados (puede tener muchos huecos, días desbalanceados, etc.). La optimización viene en Fase 6.

---

## 📋 FASE 6: Motor de Horarios - Parte 2 (Optimización)
**Duración:** Días 18-22  
**Objetivo:** Implementar optimización de horarios con Algoritmos Genéticos para mejorar calidad

### 6.1 Restricciones Blandas (Soft Constraints)

#### Día 18: Definir función de fitness

**Concepto:** Las restricciones blandas son preferencias que queremos maximizar pero no son obligatorias. La "calidad" de un horario se mide con una función fitness.

**Archivo:** `app/services/schedule_engine/fitness.py`

##### Criterios de calidad a optimizar:

**1. Minimizar huecos (gaps) entre clases**
```python
def calculate_gaps_penalty(schedule: Schedule) -> float:
    """
    Penalizar huecos entre clases del mismo día.
    
    Ejemplo:
    - Clase 7am-9am, luego clase 2pm-4pm = Gap de 5 horas (malo)
    - Clase 7am-9am, luego clase 9am-11am = Gap de 0 horas (bueno)
    
    Retorna: penalización (mayor = peor)
    """
    total_gap_hours = 0
    
    for day in range(7):  # Lunes a Domingo
        day_classes = schedule.get_classes_for_day(day)
        day_classes.sort(key=lambda c: c.start_time)
        
        for i in range(len(day_classes) - 1):
            gap = (day_classes[i+1].start_time - day_classes[i].end_time).hours
            total_gap_hours += gap
    
    return total_gap_hours * 10  # Peso: cada hora de gap penaliza 10 puntos
```

**2. Equilibrar distribución de días**
```python
def calculate_balance_penalty(schedule: Schedule) -> float:
    """
    Penalizar distribución desbalanceada en la semana.
    
    Ideal: clases distribuidas uniformemente (ej: 3 días con 2 clases cada uno)
    Malo: todas las clases en 2 días
    
    Retorna: penalización basada en desviación estándar
    """
    classes_per_day = [0] * 7
    
    for slot in schedule.slots:
        classes_per_day[slot.day_of_week] += 1
    
    # Calcular desviación estándar
    mean = sum(classes_per_day) / len(classes_per_day)
    variance = sum((x - mean) ** 2 for x in classes_per_day) / len(classes_per_day)
    std_dev = variance ** 0.5
    
    return std_dev * 15  # Peso
```

**3. Preferencia de horarios**
```python
def calculate_time_preference_penalty(schedule: Schedule) -> float:
    """
    Penalizar clases muy temprano o muy tarde.
    
    Preferido: 8am-6pm
    Aceptable: 7am-7pm
    No deseado: antes 7am o después 7pm
    """
    penalty = 0
    
    for slot in schedule.slots:
        if slot.start_time.hour < 7:
            penalty += 20
        elif slot.start_time.hour > 18:
            penalty += 10
    
    return penalty
```

**4. Días libres**
```python
def calculate_free_days_bonus(schedule: Schedule) -> float:
    """
    Bonificar tener al menos un día completamente libre.
    
    Retorna: bonus negativo (mejora fitness)
    """
    days_with_classes = len([d for d in range(7) 
                            if schedule.has_classes_on_day(d)])
    
    free_days = 7 - days_with_classes
    
    return -free_days * 20  # Cada día libre bonifica -20
```

**Función fitness total:**
```python
def calculate_fitness(schedule: Schedule) -> float:
    """
    Calcula fitness total del horario.
    Menor = mejor (penalizaciones suman, bonificaciones restan)
    
    Retorna: score total
    """
    score = 0
    
    score += calculate_gaps_penalty(schedule)
    score += calculate_balance_penalty(schedule)
    score += calculate_time_preference_penalty(schedule)
    score += calculate_free_days_bonus(schedule)
    
    return score
```

### 6.2 Algoritmo Genético

#### Día 19-20: Implementación con DEAP

**Instalación:**
```bash
pip install deap
```

**Archivo:** `app/services/schedule_engine/genetic_optimizer.py`

##### Componentes del Algoritmo Genético:

**1. Representación del individuo (cromosoma)**
```python
"""
Un individuo = Un horario completo
Representación: Lista de secciones asignadas

Ejemplo:
individuo = [section_12, section_45, section_78, section_23, section_90]
            ↓
Significa: cursar la sección 12 de Cálculo I, sección 45 de Física, etc.
"""

def create_individual(student: Student, available_sections: List[Section]) -> List[int]:
    """
    Crea un individuo aleatorio (horario aleatorio válido).
    Asegura que cumple restricciones duras.
    """
    individual = []
    
    # Para cada asignatura seleccionada, elegir una sección aleatoria
    for subject_id in student.selected_subjects:
        subject_sections = [s for s in available_sections 
                          if s.subject_id == subject_id]
        # Elegir sección aleatoria que no cause choques
        selected = random.choice(subject_sections)
        individual.append(selected.id)
    
    return individual
```

**2. Población inicial**
```python
def create_population(size: int, student: Student, sections: List[Section]) -> List:
    """
    Genera población inicial de N individuos.
    """
    population = []
    
    for _ in range(size):
        individual = create_individual(student, sections)
        population.append(individual)
    
    return population

# Parámetros típicos:
POPULATION_SIZE = 100
```

**3. Evaluación (fitness)**
```python
def evaluate(individual: List[int]) -> Tuple[float,]:
    """
    Evalúa un individuo usando función de fitness.
    DEAP requiere retornar tupla.
    """
    schedule = convert_to_schedule(individual)
    fitness_score = calculate_fitness(schedule)
    return (fitness_score,)  # Tupla requerida por DEAP
```

**4. Operador de Selección**
```python
"""
Selecciona individuos para reproducción.
Métodos comunes:
- Tournament selection (torneo)
- Roulette wheel (ruleta)
"""

# DEAP ya incluye operadores, solo configurar:
toolbox.register("select", tools.selTournament, tournsize=3)
```

**5. Operador de Cruce (Crossover)**
```python
def custom_crossover(ind1: List[int], ind2: List[int]) -> Tuple[List[int], List[int]]:
    """
    Combina dos individuos (padres) para crear dos hijos.
    
    Estrategia: Para cada asignatura, heredar sección de uno de los padres.
    """
    child1, child2 = [], []
    
    for i in range(len(ind1)):
        if random.random() < 0.5:
            child1.append(ind1[i])
            child2.append(ind2[i])
        else:
            child1.append(ind2[i])
            child2.append(ind1[i])
    
    return child1, child2

toolbox.register("mate", custom_crossover)
```

**6. Operador de Mutación**
```python
def custom_mutation(individual: List[int]) -> Tuple[List[int],]:
    """
    Muta un individuo cambiando aleatoriamente una sección.
    """
    if random.random() < MUTATION_RATE:
        # Elegir posición aleatoria
        idx = random.randint(0, len(individual) - 1)
        
        # Cambiar por otra sección de la misma asignatura
        subject_id = get_subject_id_from_section(individual[idx])
        alternative_sections = get_sections_for_subject(subject_id)
        individual[idx] = random.choice(alternative_sections).id
    
    return (individual,)

MUTATION_RATE = 0.1  # 10% de probabilidad

toolbox.register("mutate", custom_mutation)
```

**7. Algoritmo principal**
```python
class GeneticScheduleOptimizer:
    """
    Optimiza horarios usando Algoritmo Genético.
    """
    
    def __init__(
        self,
        student: Student,
        available_sections: List[Section],
        population_size: int = 100,
        generations: int = 50
    ):
        self.student = student
        self.sections = available_sections
        self.population_size = population_size
        self.generations = generations
        
        self._setup_deap()
    
    def _setup_deap(self):
        """Configurar DEAP toolbox"""
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
        
        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", self._create_individual)
        self.toolbox.register("population", tools.initRepeat, 
                            list, self.toolbox.individual)
        self.toolbox.register("evaluate", self._evaluate)
        self.toolbox.register("mate", custom_crossover)
        self.toolbox.register("mutate", custom_mutation)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
    
    def optimize(self) -> ScheduleSolution:
        """
        Ejecuta algoritmo genético.
        """
        # Crear población inicial
        population = self.toolbox.population(n=self.population_size)
        
        # Evaluar población inicial
        fitnesses = map(self.toolbox.evaluate, population)
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit
        
        # Evolucionar por N generaciones
        for generation in range(self.generations):
            # Selección
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))
            
            # Cruce
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.7:  # 70% probabilidad de cruce
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
            
            # Mutación
            for mutant in offspring:
                if random.random() < 0.2:  # 20% probabilidad de mutación
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values
            
            # Evaluar individuos con fitness inválido
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            
            # Reemplazar población
            population[:] = offspring
            
            # Logging progreso
            best_ind = tools.selBest(population, 1)[0]
            print(f"Gen {generation}: Best fitness = {best_ind.fitness.values[0]}")
        
        # Retornar mejor individuo
        best_individual = tools.selBest(population, 1)[0]
        return self._convert_to_solution(best_individual)
```

### 6.3 Integración Híbrida

#### Día 21: Combinar OR-Tools + Algoritmo Genético

**Archivo:** `app/services/schedule_engine/hybrid_engine.py`

**Estrategia:**
1. **Fase 1:** Usar OR-Tools CP-SAT para encontrar **cualquier** solución viable (restricciones duras)
2. **Fase 2:** Usar AG para **mejorar** la solución optimizando restricciones blandas
```python
class HybridScheduleEngine:
    """
    Motor híbrido que combina Constraint Solver + Genetic Algorithm.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_optimized_schedule(
        self,
        student_id: int,
        selected_subject_ids: List[int],
        optimization_level: str = "high"
    ) -> ScheduleSolution:
        """
        Genera horario optimizado usando enfoque híbrido.
        
        Args:
            optimization_level: "none" | "low" | "medium" | "high"
        """
        # 1. Cargar datos
        student = self._load_student(student_id)
        sections = self._load_sections(selected_subject_ids)
        
        # 2. FASE 1: Encontrar solución viable con CP-SAT
        logger.info("Phase 1: Finding feasible solution with CP-SAT...")
        constraint_solver = ConstraintScheduleSolver(student, sections)
        constraint_solver.create_variables()
        constraint_solver.add_constraints()
        initial_solution = constraint_solver.solve()
        
        if not initial_solution.is_feasible:
            # No hay solución viable
            return initial_solution
        
        # 3. FASE 2: Optimizar con AG (si se solicita)
        if optimization_level == "none":
            return initial_solution
        
        logger.info("Phase 2: Optimizing with Genetic Algorithm...")
        
        # Configurar parámetros según nivel
        ga_params = self._get_ga_parameters(optimization_level)
        
        genetic_optimizer = GeneticScheduleOptimizer(
            student=student,
            available_sections=sections,
            population_size=ga_params['population'],
            generations=ga_params['generations']
        )
        
        optimized_solution = genetic_optimizer.optimize()
        
        # 4. Comparar y retornar mejor
        if optimized_solution.quality_score < initial_solution.quality_score:
            logger.info("AG improved solution")
            return optimized_solution
        else:
            logger.info("CP-SAT solution was already optimal")
            return initial_solution
    
    def _get_ga_parameters(self, level: str) -> dict:
        """Parámetros de AG según nivel de optimización"""
        params = {
            "low": {"population": 50, "generations": 20},
            "medium": {"population": 100, "generations": 50},
            "high": {"population": 200, "generations": 100}
        }
        return params.get(level, params["medium"])
```

### 6.4 Actualizar Endpoint

**Archivo:** `app/api/v1/schedules.py`
```python
@router.post("/api/v1/schedules/generate-optimized")
def generate_optimized_schedule(
    request: OptimizedScheduleRequest,
    db: Session = Depends(get_db)
) -> ScheduleSolution:
    """
    Genera horario optimizado usando motor híbrido.
    
    Body:
    {
        "student_id": 123,
        "selected_subject_ids": [1, 2, 3, 4, 5],
        "optimization_level": "high"  // "none" | "low" | "medium" | "high"
    }
    """
    engine = HybridScheduleEngine(db)
    solution = engine.generate_optimized_schedule(
        request.student_id,
        request.selected_subject_ids,
        request.optimization_level
    )
    return solution
```

### 6.5 Métricas de Calidad

#### Día 22: Sistema de métricas

**Archivo:** `app/services/schedule_engine/metrics.py`
```python
@dataclass
class ScheduleQualityMetrics:
    """Métricas de calidad de un horario"""
    
    # Métricas básicas
    total_gaps_hours: float
    avg_gap_per_day: float
    days_with_classes: int
    free_days: int
    
    # Métricas de distribución
    balance_score: float  # 0-100, mayor = mejor distribuido
    earliest_class: time
    latest_class: time
    
    # Métricas avanzadas
    classes_before_8am: int
    classes_after_6pm: int
    max_classes_per_day: int
    
    # Score final
    overall_quality_score: float  # 0-100, mayor = mejor
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para API"""
        return {
            "gaps": {
                "total_hours": self.total_gaps_hours,
                "average_per_day": self.avg_gap_per_day
            },
            "distribution": {
                "days_with_classes": self.days_with_classes,
                "free_days": self.free_days,
                "balance_score": self.balance_score
            },
            "time_range": {
                "earliest": str(self.earliest_class),
                "latest": str(self.latest_class),
                "early_classes": self.classes_before_8am,
                "late_classes": self.classes_after_6pm
            },
            "overall_score": self.overall_quality_score
        }

def calculate_schedule_metrics(schedule: Schedule) -> ScheduleQualityMetrics:
    """Calcula todas las métricas de un horario"""
    # Implementar cálculos...
    pass
```

### 6.6 Comparación de Algoritmos

**Crear:** `scripts/compare_algorithms.py`

Script para comparar rendimiento de CP-SAT vs AG:
```python
"""
Ejecuta múltiples casos de prueba y compara:
- Tiempo de ejecución
- Calidad de soluciones
- Tasa de éxito
"""

def run_comparison():
    test_cases = generate_test_cases(count=50)
    
    results = {
        "cp_sat_only": [],
        "genetic_only": [],
        "hybrid": []
    }
    
    for test_case in test_cases:
        # Probar cada método
        # Registrar métricas
        pass
    
    # Generar reporte comparativo
    generate_report(results)
```

### 6.7 Tests

**Archivo:** `tests/test_genetic_optimizer.py`

- [ ] Test: AG mejora fitness sobre generaciones
- [ ] Test: AG respeta restricciones duras
- [ ] Test: Convergencia del algoritmo
- [ ] Test: Comparación con solución aleatoria

**Archivo:** `tests/test_hybrid_engine.py`

- [ ] Test: Motor híbrido genera mejor solución que CP-SAT solo
- [ ] Test: Fallback a CP-SAT si AG no mejora
- [ ] Test: Diferentes niveles de optimización

### 6.8 Deliverables Fase 6
- [ ] `GeneticScheduleOptimizer` implementado
- [ ] `HybridScheduleEngine` funcionando
- [ ] Función fitness con múltiples criterios
- [ ] Sistema de métricas de calidad
- [ ] Endpoint de generación optimizada
- [ ] Comparación de algoritmos documentada
- [ ] Tests pasando
- [ ] Documentación técnica:
  - Explicación del AG
  - Parámetros y tuning
  - Comparativa de resultados
  - Ejemplos de mejoras logradas

### Documentación requerida

**Crear:** `docs/motor-horarios.md`

Debe incluir:
- Arquitectura del motor (diagrama de flujo)
- Restricciones duras vs blandas
- Función fitness explicada
- Parámetros del AG
- Resultados de comparación
- Guía de tuning

### Métricas objetivo a lograr

| Métrica                     | Objetivo      | 
|-----------------------------|---------------|
| Tiempo generación (CP-SAT)  | < 2 segundos  |
| Tiempo optimización (AG)    | < 10 segundos |
| Mejora fitness AG vs CP-SAT | > 30%         |
| Huecos promedio             | < 2 horas/día |
| Balance de días             | Score > 70    |

### Recursos de aprendizaje
- DEAP documentation: https://deap.readthedocs.io
- Genetic Algorithms: concepts and applications
- Fitness function design
- Hybrid metaheuristics
- Multi-objective optimization

---

## 📋 FASE 7: Workers Asíncronos
**Duración:** Días 23-25  
**Objetivo:** Implementar procesamiento asíncrono para generación de horarios en background

### 7.1 Setup Celery + Redis

#### Día 23: Configuración

**Instalación:**
```bash
pip install celery redis
```

**Docker Compose actualizado:**

**Archivo:** `docker-compose.yml`
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: sghu
      POSTGRES_USER: sghu_user
      POSTGRES_PASSWORD: sghu_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

**Configuración de Celery:**

**Archivo:** `app/core/celery_app.py`
```python
from celery import Celery
from app.config import settings

celery_app = Celery(
    "sghu",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.workers.tasks']
)

# Configuración
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Bogota',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutos máximo por task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000
)
```

**Actualizar config.py:**
```python
class Settings(BaseSettings):
    # ... configs existentes
    REDIS_URL: str = "redis://localhost:6379/0"
```

### 7.2 Tasks de Celery

#### Archivo: `app/workers/tasks.py`

**Task 1: Generar horario individual**
```python
from app.core.celery_app import celery_app
from app.services.schedule_engine.hybrid_engine import HybridScheduleEngine
from app.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="generate_student_schedule")
def generate_student_schedule_task(
    self,
    student_id: int,
    selected_subject_ids: List[int],
    optimization_level: str = "medium"
):
    """
    Task asíncrono para generar horario de un estudiante.
    
    Args:
        self: Task instance (por bind=True)
        student_id: ID del estudiante
        selected_subject_ids: IDs de asignaturas seleccionadas
        optimization_level: Nivel de optimización
    
    Returns:
        dict con resultado de generación
    """
    db = SessionLocal()
    
    try:
        # Actualizar estado
        self.update_state(
            state='PROCESSING',
            meta={'current': 0, 'total': 2, 'status': 'Iniciando generación...'}
        )
        
        # Generar horario
        engine = HybridScheduleEngine(db)
        
        self.update_state(
            state='PROCESSING',
            meta={'current': 1, 'total': 2, 'status': 'Resolviendo restricciones...'}
        )
        
        solution = engine.generate_optimized_schedule(
            student_id=student_id,
            selected_subject_ids=selected_subject_ids,
            optimization_level=optimization_level
        )
        
        # Persistir resultado
        self.update_state(
            state='PROCESSING',
            meta={'current': 2, 'total': 2, 'status': 'Guardando resultado...'}
        )
        
        # Guardar en BD
        schedule_id = save_schedule_to_db(db, solution)
        
        logger.info(f"Schedule generated successfully for student {student_id}")
        
        return {
            'status': 'success',
            'student_id': student_id,
            'schedule_id': schedule_id,
            'is_feasible': solution.is_feasible,
            'quality_score': solution.quality_score,
            'processing_time': solution.processing_time
        }
        
    except Exception as e:
        logger.error(f"Error generating schedule: {str(e)}")
        
        # Guardar error en BD
        save_error_log(db, student_id, str(e))
        
        raise  # Re-lanzar para que Celery maneje el retry
        
    finally:
        db.close()
```

**Task 2: Procesamiento en lote**
```python
@celery_app.task(name="process_enrollment_batch")
def process_enrollment_batch_task(enrollment_period_id: int):
    """
    Procesa matrículas de múltiples estudiantes en lote.
    Genera horarios para todos los estudiantes que solicitaron matrícula.
    """
    db = SessionLocal()
    
    try:
        # Obtener todas las matrículas pendientes
        pending_enrollments = get_pending_enrollments(db, enrollment_period_id)
        
        results = {
            'total': len(pending_enrollments),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for enrollment in pending_enrollments:
            try:
                # Delegar a task individual
                task = generate_student_schedule_task.delay(
                    student_id=enrollment.student_id,
                    selected_subject_ids=enrollment.selected_subject_ids,
                    optimization_level="medium"
                )
                
                results['details'].append({
                    'student_id': enrollment.student_id,
                    'task_id': task.id,
                    'status': 'queued'
                })
                
            except Exception as e:
                logger.error(f"Error queueing student {enrollment.student_id}: {e}")
                results['failed'] += 1
        
        return results
        
    finally:
        db.close()
```

**Task 3: Sincronización con Moodle (simulado)**
```python
@celery_app.task(name="sync_with_moodle")
def sync_with_moodle_task(schedule_id: int):
    """
    Sincroniza horario generado con Moodle (simulado).
    
    En producción real:
    - Crearía cursos en Moodle vía API
    - Inscribiría estudiantes
    - Sincronizaría calendario
    """
    db = SessionLocal()
    
    try:
        schedule = get_schedule_by_id(db, schedule_id)
        
        # Simulación de llamadas a API Moodle
        for slot in schedule.slots:
            section = get_section(db, slot.section_id)
            
            # Simular creación de curso
            moodle_course = {
                'course_code': section.subject.code,
                'course_name': section.subject.name,
                'section_number': section.section_number
            }
            
            logger.info(f"Would create Moodle course: {moodle_course}")
            
            # Simular inscripción
            logger.info(f"Would enroll student {schedule.student_id} in course")
        
        # Marcar como sincronizado
        mark_schedule_as_synced(db, schedule_id)
        
        return {'status': 'success', 'schedule_id': schedule_id}
        
    finally:
        db.close()
```

### 7.3 API Endpoints Asíncronos

#### Día 24: Endpoints para workers

**Archivo:** `app/api/v1/async_schedules.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from celery.result import AsyncResult
from app.workers.tasks import (
    generate_student_schedule_task,
    process_enrollment_batch_task
)

router = APIRouter()

@router.post("/api/v1/async/schedules/generate")
def request_schedule_generation(
    request: AsyncScheduleRequest,
    db: Session = Depends(get_db)
):
    """
    Solicita generación de horario de forma asíncrona.
    Retorna task_id para consultar estado.
    
    Body:
    {
        "student_id": 123,
        "selected_subject_ids": [1, 2, 3, 4, 5],
        "optimization_level": "high"
    }
    
    Response:
    {
        "task_id": "a1b2c3d4-...",
        "status": "queued",
        "message": "Solicitud recibida. Usa task_id para consultar estado."
    }
    """
    # Validaciones previas (opcional)
    # - Verificar que estudiante existe
    # - Verificar que materias son válidas
    
    # Encolar task
    task = generate_student_schedule_task.delay(
        student_id=request.student_id,
        selected_subject_ids=request.selected_subject_ids,
        optimization_level=request.optimization_level
    )
    
    return {
        "task_id": task.id,
        "status": "queued",
        "message": "Schedule generation queued successfully"
    }

@router.get("/api/v1/async/schedules/status/{task_id}")
def get_schedule_generation_status(task_id: str):
    """
    Consulta el estado de una tarea de generación.
    
    Estados posibles:
    - PENDING: En cola
    - PROCESSING: Ejecutándose
    - SUCCESS: Completado exitosamente
    - FAILURE: Falló
    - RETRY: Reintentando
    
    Response cuando está en progreso:
    {
        "task_id": "...",
        "state": "PROCESSING",
        "progress": {
            "current": 1,
            "total": 2,
            "status": "Resolviendo restricciones..."
        }
    }
    
    Response cuando completó:
    {
        "task_id": "...",
        "state": "SUCCESS",
        "result": {
            "status": "success",
            "student_id": 123,
            "schedule_id": 456,
            "is_feasible": true,
            "quality_score": 85.5
        }
    }
    """
    task_result = AsyncResult(task_id)
    
    if task_result.state == 'PENDING':
        response = {
            'task_id': task_id,
            'state': task_result.state,
            'status': 'Task is queued and waiting for execution'
        }
    elif task_result.state == 'PROCESSING':
        response = {
            'task_id': task_id,
            'state': task_result.state,
            'progress': task_result.info
        }
    elif task_result.state == 'SUCCESS':
        response = {
            'task_id': task_id,
            'state': task_result.state,
            'result': task_result.result
        }
    elif task_result.state == 'FAILURE':
        response = {
            'task_id': task_id,
            'state': task_result.state,
            'error': str(task_result.info)
        }
    else:
        response = {
            'task_id': task_id,
            'state': task_result.state
        }
    
    return response

@router.get("/api/v1/async/schedules/result/{task_id}")
def get_schedule_result(task_id: str, db: Session = Depends(get_db)):
    """
    Obtiene el horario generado una vez completada la tarea.
    Solo funciona si el task está en estado SUCCESS.
    """
    task_result = AsyncResult(task_id)
    
    if task_result.state != 'SUCCESS':
        raise HTTPException(
            status_code=400,
            detail=f"Task is not completed. Current state: {task_result.state}"
        )
    
    result = task_result.result
    schedule_id = result.get('schedule_id')
    
    if not schedule_id:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Obtener horario completo de BD
    schedule = get_full_schedule(db, schedule_id)
    
    return schedule

@router.post("/api/v1/async/enrollment/process-batch")
def process_enrollment_batch(
    enrollment_period_id: int,
    db: Session = Depends(get_db)
):
    """
    Procesa lote completo de matrículas.
    Genera horarios para todos los estudiantes pendientes.
    """
    # Verificar que período existe
    period = get_enrollment_period(db, enrollment_period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Enrollment period not found")
    
    # Encolar procesamiento
    task = process_enrollment_batch_task.delay(enrollment_period_id)
    
    return {
        "task_id": task.id,
        "status": "queued",
        "message": "Batch processing started"
    }
```

### 7.4 Monitoreo y Logging

#### Día 25: Sistema de monitoreo

**Flower (Monitor web para Celery):**
```bash
pip install flower
```

**Agregar a docker-compose.yml:**
```yaml
  flower:
    image: mher/flower
    command: celery --broker=redis://redis:6379/0 flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis
```

**Acceso:** `http://localhost:5555`

**Logging mejorado:**

**Archivo:** `app/core/logging_config.py`
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configurar logging para workers"""
    
    # Logger para tasks
    task_logger = logging.getLogger('celery.tasks')
    task_logger.setLevel(logging.INFO)
    
    # Handler para archivo
    handler = RotatingFileHandler(
        'logs/celery_tasks.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    task_logger.addHandler(handler)
```

**Endpoint de monitoreo:**
```python
@router.get("/api/v1/async/stats")
def get_worker_stats():
    """
    Estadísticas de workers y cola.
    """
    from app.core.celery_app import celery_app
    
    inspect = celery_app.control.inspect()
    
    stats = {
        'active_workers': len(inspect.active() or {}),
        'active_tasks': inspect.active(),
        'scheduled_tasks': inspect.scheduled(),
        'reserved_tasks': inspect.reserved()
    }
    
    return stats
```

### 7.5 Manejo de Errores y Reintentos

**Configuración de reintentos:**
```python
@celery_app.task(
    bind=True,
    name="generate_student_schedule",
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 5},
    retry_backoff=True
)
def generate_student_schedule_task(self, ...):
    # Task con reintentos automáticos
    pass
```

**Manejo de fallas:**
```python
@celery_app.task(bind=True)
def my_task(self):
    try:
        # Lógica del task
        pass
    except SoftTimeLimitExceeded:
        # Task excedió tiempo límite
        logger.error("Task timed out")
        cleanup()
        raise
    except Exception as exc:
        # Log error
        logger.error(f"Task failed: {exc}")
        
        # Reintentar
        raise self.retry(exc=exc, countdown=60)
```

### 7.6 Comandos para Correr Workers

**Crear:** `scripts/start_worker.sh`
```bash
#!/bin/bash

# Iniciar worker de Celery
celery -A app.core.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=100 \
    --logfile=logs/celery_worker.log
```

**Crear:** `scripts/start_beat.sh` (para tasks periódicos, opcional)
```bash
#!/bin/bash

# Iniciar Celery Beat (scheduler)
celery -A app.core.celery_app beat \
    --loglevel=info \
    --logfile=logs/celery_beat.log
```

### 7.7 Tests

**Archivo:** `tests/test_celery_tasks.py`
```python
import pytest
from app.workers.tasks import generate_student_schedule_task

def test_schedule_generation_task(db_session):
    """Test task de generación"""
    
    # Crear datos de prueba
    student_id = create_test_student(db_session)
    subject_ids = [1, 2, 3]
    
    # Ejecutar task (síncrono para test)
    result = generate_student_schedule_task(
        student_id=student_id,
        selected_subject_ids=subject_ids,
        optimization_level="low"
    )
    
    assert result['status'] == 'success'
    assert 'schedule_id' in result

def test_task_failure_handling():
    """Test manejo de errores"""
    
    # Ejecutar con datos inválidos
    result = generate_student_schedule_task(
        student_id=999999,  # No existe
        selected_subject_ids=[],
        optimization_level="low"
    )
    
    # Debería fallar gracefully
    pass
```

### 7.8 Deliverables Fase 7
- [ ] Celery + Redis configurados y funcionando
- [ ] Tasks asíncronos implementados:
  - Generación individual
  - Procesamiento en lote
  - Sincronización Moodle (simulada)
- [ ] Endpoints asíncronos funcionando:
  - POST para encolar
  - GET para estado
  - GET para resultado
- [ ] Flower corriendo para monitoreo
- [ ] Sistema de logging configurado
- [ ] Manejo de errores y reintentos
- [ ] Scripts de inicio de workers
- [ ] Tests de tasks
- [ ] Documentación:
  - Arquitectura asíncrona
  - Cómo correr workers
  - Monitoreo de tasks
  - Troubleshooting

### Documentación requerida

**Crear:** `docs/workers-asincrono.md`

Debe incluir:
- Diagrama de flujo asíncrono
- Cómo funciona Celery + Redis
- Estados de tasks
- Cómo escalar workers
- Troubleshooting común

### Comandos útiles
```bash
# Iniciar todos los servicios
docker-compose up -d

# Iniciar worker
celery -A app.core.celery_app worker --loglevel=info

# Iniciar Flower
celery -A app.core.celery_app flower

# Ver estado de workers
celery -A app.core.celery_app inspect active

# Purgar cola
celery -A app.core.celery_app purge
```

### Recursos de aprendizaje
- Celery documentation: https://docs.celeryq.dev
- Redis as message broker
- Async task patterns
- Worker scaling strategies
- Monitoring and debugging async tasks

---

## 📋 FASE 8: Testing y Refinamiento
**Duración:** Días 26-28  
**Objetivo:** Asegurar calidad del código con tests completos y optimizar performance

### 8.1 Estrategia de Testing

#### Tipos de tests a implementar:

**1. Tests Unitarios**
- Funciones individuales
- Servicios de negocio
- Validaciones
- Algoritmos (fitness, mutación, etc.)

**2. Tests de Integración**
- Endpoints completos
- Flujos de múltiples servicios
- Interacción con BD

**3. Tests de Performance**
- Tiempo de generación de horarios
- Carga de requests simultáneos
- Consultas a BD

### 8.2 Setup de Testing

#### Día 26: Configuración

**Instalación:**
```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

**Estructura de tests:**
```
tests/
├── __init__.py
├── conftest.py          # Fixtures compartidos
├── unit/
│   ├── test_validation_service.py
│   ├── test_constraint_solver.py
│   ├── test_genetic_optimizer.py
│   └── test_fitness_functions.py
├── integration/
│   ├── test_enrollment_flow.py
│   ├── test_schedule_generation_flow.py
│   └── test_async_tasks.py
└── performance/
    ├── test_solver_performance.py
    └── test_load_testing.py
```
Fixtures básicos necesarios:

engine: Engine de BD de prueba
db_session: Sesión de BD para cada test
client: Cliente de prueba de FastAPI
sample_student: Estudiante de prueba
sample_sections: Secciones de prueba

8.3 Tests Unitarios
Tests de ValidationService:

 test_validate_financial_status_no_debt: Estudiante sin deuda puede matricularse
 test_validate_financial_status_with_debt: Estudiante con deuda no puede matricularse
 test_validate_prerequisites_met: Prerrequisitos cumplidos
 test_validate_prerequisites_not_met: Prerrequisitos NO cumplidos
 test_validate_credit_limit_within_range: Créditos dentro del límite
 test_validate_credit_limit_exceeds: Excede límite de créditos
 test_validate_section_capacity_available: Hay cupos disponibles
 test_validate_section_capacity_full: Sección llena
 test_validate_schedule_conflicts_none: Sin choques de horario
 test_validate_schedule_conflicts_detected: Detectar choques de horario

Tests de ConstraintSolver:

 test_solve_simple_case: Resolver caso simple sin conflictos
 test_solve_with_time_conflicts: Manejar conflictos de horario
 test_solve_infeasible_case: Caso sin solución
 test_one_section_per_subject_constraint: Solo una sección por asignatura
 test_capacity_constraint: No asignar secciones llenas

Tests de GeneticOptimizer:

 test_optimizer_improves_fitness: AG mejora fitness sobre generaciones
 test_optimizer_respects_hard_constraints: AG respeta restricciones duras
 test_crossover_operation: Operador de crossover funciona
 test_mutation_operation: Operador de mutación funciona

Tests de Fitness Functions:

 test_gaps_penalty_no_gaps: Sin huecos = penalización baja
 test_gaps_penalty_with_gaps: Con huecos = penalización alta
 test_balance_penalty_balanced: Horario balanceado
 test_balance_penalty_unbalanced: Horario desbalanceado
 test_time_preference_penalty_good_hours: Clases en horas preferidas
 test_time_preference_penalty_early_late: Clases muy temprano/tarde
 test_free_days_bonus: Días libres dan bonificación
 test_overall_fitness_integration: Función fitness integra todos los componentes

8.4 Tests de Integración
Día 27: Tests end-to-end
Test de flujo completo de matrícula:

Consultar oferta académica
Seleccionar materias
Validar selección
Generar horario
Confirmar matrícula

Tests de casos especiales:

 test_enrollment_with_financial_block: Estudiante con deuda bloqueado
 test_enrollment_with_prerequisite_missing: Sin prerrequisitos
 test_async_schedule_generation: Generación asíncrona completa
 test_batch_processing: Procesamiento en lote
 test_task_failure_handling: Manejo de errores en tasks

8.5 Tests de Performance
Tests de velocidad:

 test_constraint_solver_speed: CP-SAT < 2 segundos
 test_genetic_optimizer_speed: AG < 10 segundos
 test_hybrid_engine_speed: Motor híbrido < 12 segundos
 test_scalability_by_subjects: Escalabilidad por número de materias

Tests de carga:

 test_concurrent_requests: 50 requests simultáneos < 5s
 test_database_query_performance: Queries < 200ms

8.6 Optimizaciones
Día 28: Refinamiento y optimización
1. Índices de Base de Datos
Crear archivo: scripts/create_indexes.sql
Índices necesarios:

idx_students_program en students(program_id)
idx_students_code en students(code)
idx_academic_history_student en academic_history(student_id)
idx_academic_history_subject en academic_history(subject_id)
idx_course_sections_period en course_sections(period_id)
idx_section_schedules_section en section_schedules(section_id)
idx_student_enrollments_student en student_enrollments(student_id)
idx_generated_schedules_enrollment en generated_schedules(enrollment_id)

2. Caching
Implementar:

Cache en memoria con @lru_cache para prerrequisitos
Cache en Redis para oferta académica (TTL: 1 hora)
Cache de resultados de validaciones frecuentes

3. Optimización de Consultas
Aplicar:

Eager loading con joinedload() para evitar N+1
Paginación en listados grandes (limit/offset)
Índices en columnas de búsqueda frecuente

4. Paginación en Endpoints
Implementar parámetros skip y limit en:

GET /course-sections
GET /students
GET /subjects

8.7 Coverage Report
Comandos:


# Ejecutar tests con coverage
pytest --cov=app --cov-report=html --cov-report=term

# Ver reporte
open htmlcov/index.html


Objetivo de coverage:

Total: > 80%
Servicios críticos (validaciones, motor): > 90%
Endpoints: > 85%

8.8 Deliverables Fase 8

 Tests unitarios completos (validaciones, solver, AG, fitness)
 Tests de integración (flujos completos)
 Tests de performance (tiempos de ejecución)
 Tests de carga (requests concurrentes)
 Coverage report > 80%
 Índices de BD creados
 Sistema de caching implementado
 Optimizaciones de queries aplicadas
 Documentación de performance:

Benchmarks
Tiempos objetivo vs alcanzados
Cuellos de botella identificados
Optimizaciones aplicadas

## Checklist de Calidad del Código

### Tests
- [ ] Tests unitarios pasando
- [ ] Tests de integración pasando
- [ ] Coverage > 80%
- [ ] No hay tests skippeados sin justificación

### Performance
- [ ] CP-SAT < 2s
- [ ] AG < 10s
- [ ] Motor híbrido < 12s
- [ ] Endpoints responden < 500ms

### Base de Datos
- [ ] Índices creados en columnas frecuentes
- [ ] No hay problema N+1
- [ ] Uso de eager loading donde corresponde
- [ ] Paginación en listados grandes

### Código
- [ ] Sin código duplicado
- [ ] Funciones < 50 líneas
- [ ] Nombres descriptivos
- [ ] Docstrings en funciones públicas
- [ ] Type hints en funciones

### Seguridad
- [ ] Validación de inputs
- [ ] Sanitización de datos
- [ ] Manejo de errores sin exponer detalles internos
- [ ] Logs sin información sensible

MétricaObjetivoCoverage total> 80%
Coverage servicios críticos > 90%
CP-SAT tiempo < 2s
AG tiempo < 10s
Motor híbrido < 12s
Endpoints response < 500ms
Queries DB < 200ms



Recursos de aprendizaje

Pytest documentation: https://docs.pytest.org
SQLAlchemy performance tips
FastAPI testing guide
Load testing with locust
Code coverage best practices


📋 FASE 9: Simulador Frontend
Duración: Días 29-30
Objetivo: Crear scripts que simulen interacción del frontend con la API
9.1 Script de Simulación Individual
Día 29: Flujo de estudiante individual
Archivo a crear: scripts/simulate_student_flow.py
Funcionalidad:
Simula el flujo completo de un estudiante matriculándose, imitando las interacciones que haría un frontend real.
Clase principal: StudentFlowSimulator
Pasos del flujo a simular:

step1_view_profile(): Ver perfil del estudiante

GET /students/{id}
Mostrar: nombre, programa, semestre


step2_check_financial_status(): Verificar estado financiero

GET /students/{id}/enrollment-status
Verificar si puede matricularse


step3_view_academic_offer(): Consultar oferta académica

GET /course-sections?period_id=1
Listar secciones disponibles


step4_get_eligible_subjects(): Obtener materias elegibles

GET /students/{id}/eligible-subjects
Filtrar materias que puede cursar


step5_select_subjects(): Seleccionar materias

Elegir 5 materias de las elegibles


step6_validate_selection(): Validar selección

POST /enrollment/validate
Verificar todas las validaciones


step7_request_schedule_generation(): Solicitar generación

POST /async/schedules/generate
Obtener task_id


step8_wait_for_schedule(): Esperar resultado

GET /async/schedules/status/{task_id} (polling)
GET /async/schedules/result/{task_id}


step9_review_schedule(): Revisar horario

Analizar calidad del horario
Mostrar estadísticas


step10_confirm_enrollment(): Confirmar matrícula

POST /enrollment/confirm
Completar proceso



Funcionalidades adicionales:

Logging detallado de cada paso
Medición de tiempos
Guardado de log en JSON
Manejo de errores

Uso:

# Simular un estudiante
python scripts/simulate_student_flow.py --student-id 1

# Con guardado de log
python scripts/simulate_student_flow.py --student-id 1 --save-log


9.2 Script de Carga Masiva
Día 30: Simulación de múltiples estudiantes
Archivo a crear: scripts/simulate_mass_enrollment.py

Funcionalidad:
Simula matrícula masiva de múltiples estudiantes concurrentemente para testing de performance y carga del sistema.
Clase principal: MassEnrollmentSimulator
Características:

-Procesamiento concurrente con ThreadPoolExecutor
-Configuración de número de workers
-Medición de métricas de performance
-Generación de reporte completo

Métodos principales:

1_) simulate_single_student(): Simular un estudiante

-Flujo simplificado (elegibles → generar → confirmar)
-Medición de tiempo
-Manejo de errores


2_) run_simulation(): Ejecutar simulación masiva

-Crear pool de workers
-Procesar estudiantes concurrentemente
-Mostrar progreso en tiempo real


3_) _generate_report(): Generar reporte

-Estadísticas de éxito/fallo
-Métricas de tiempo (min, max, mean, median, stdev)
-Throughput (estudiantes/segundo)
-Distribución de errores
-Quality scores



Métricas a capturar:

-Total de estudiantes procesados
-Tasa de éxito (%)
-Tiempo total
-Throughput (estudiantes/s)
-Tiempos: mínimo, máximo, promedio, mediana, desviación estándar
-Tipos de fallas: timeout, error, infeasible, sin materias
-Quality scores: min, max, mean, median

Uso:

# Simular 100 estudiantes con 10 workers
python scripts/simulate_mass_enrollment.py --students 100 --workers 10

# Con guardado de resultados
python scripts/simulate_mass_enrollment.py --students 100 --workers 10 --save-results



9.3 Script de Análisis de Resultados
Archivo a crear: scripts/analyze_simulation_results.py
Funcionalidad:
Analiza resultados de simulaciones y genera gráficos.
Características:

-Leer archivo JSON de resultados
-Generar gráficos con matplotlib:

Distribución de tiempos (histograma)
Distribución de estados (bar chart)
Distribución de quality scores (histograma)


Calcular estadísticas descriptivas
Guardar gráficos en PNG

Uso:
python 
scripts/analyze_simulation_results.py mass_enrollment_results.json


9.4 Deliverables Fase 9

 Script simulate_student_flow.py implementado
 Script simulate_mass_enrollment.py implementado
 Script analyze_simulation_results.py implementado
 Reporte de performance completo:

  -Throughput alcanzado
  -Tiempos de respuesta
  -Tasa de éxito
  -Cuellos de botella identificados

 Gráficos de análisis generados
 Documentación de uso de scripts en README
 Casos de prueba documentados

Estructura esperada de resultados
Archivo JSON generado:
json
{
  "results": [
    {
      "student_id": 1,
      "status": "success",
      "task_id": "abc123",
      "quality_score": 85.5,
      "time": 8.2
    },
    ...
  ],
  "timestamp": 1234567890
}

Métricas objetivo

Throughput                  > 5 estudiantes/segundo
Tiempo promedio             < 12 segundos
Tasa de éxito               > 95%
Timeout rate                < 2%


Testing de los simuladores
Tests a crear:

 Test de flujo individual completo
 Test de manejo de errores (estudiante inexistente)
 Test de timeout en generación
 Test de procesamiento concurrente
 Test de generación de reportes
 
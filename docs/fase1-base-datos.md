# Fase 1: Diseño de Base de Datos - Completada

## Resumen

Sistema de base de datos con 22 tablas distribuidas en 2 schemas para SGHU.

## Schemas

### Schema "source" (15 tablas)

Simula datos de sistemas externos (Odoo, Moodle):

#### Datos Institucionales

- **programs**: Programas académicos (5 esperados)
- **subjects**: Catálogo de asignaturas (100+ esperadas)
- **prerequisites**: Red de prerrequisitos
- **study_plans**: Mallas curriculares

#### Personas

- **professors**: Docentes (30+ esperados)
- **students**: Estudiantes (200+ esperados)
- **academic_history**: Historial académico
- **financial_status**: Estado financiero

#### Infraestructura

- **classrooms**: Aulas (20+ esperadas)
- **academic_rules**: Reglas institucionales

#### Oferta Académica

- **academic_periods**: Períodos académicos
- **course_sections**: Secciones ofertadas
- **section_schedules**: Horarios de secciones

#### Moodle (simulado)

- **moodle_courses**: Cursos
- **moodle_enrollments**: Inscripciones

### Schema "sghu" (7 tablas)

Datos propios del sistema:

#### Matrícula

- **enrollment_periods**: Control de períodos
- **student_enrollments**: Matrículas
- **enrollment_subjects**: Asignaturas por matrícula

#### Horarios

- **generated_schedules**: Horarios generados
- **schedule_slots**: Bloques de horario
- **schedule_conflicts**: Conflictos detectados

#### Sistema

- **processing_logs**: Logs de ejecución

## Tecnologías

- SQLAlchemy 2.0 ORM
- PostgreSQL 15
- Alembic para migraciones

## Archivos Creados

- `app/models/source/`: 7 archivos con modelos
- `app/models/sghu/`: 3 archivos con modelos
- `alembic/`: Configuración de migraciones
- `scripts/create_schemas.py`: Script de inicialización

## Migración Inicial

- **ID**: a5fc4bc98b84
- **Descripción**: Initial migration: create all tables
- **Estado**: Aplicada exitosamente

## Comandos Útiles

### Ver tablas

```bash
# Schema source
docker exec -it sghu-postgres psql -U sghu_user -d sghu -c "\dt source.*"

# Schema sghu
docker exec -it sghu-postgres psql -U sghu_user -d sghu -c "\dt sghu.*"
```

### Crear nueva migración

```bash
alembic revision --autogenerate -m "Descripción del cambio"
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1
```

## Próximos Pasos

- Fase 2: Scripts de simulación de datos
- Poblar tablas con datos realistas


# 📊 Guía para Visualizar Tablas - Presentación del Proyecto SGHU

Esta guía te ayudará a mostrar las tablas de la base de datos durante la presentación del proyecto.

## 🚀 Métodos Rápidos

### 1. Script Automatizado (Recomendado)

```bash
cd backend
./scripts/ver_tablas_presentacion.sh
```

Este script muestra:
- Estructura de tablas
- Datos de ejemplo
- Estadísticas generales
- Información organizada por schemas

### 2. Comandos Directos de PostgreSQL

#### Ver todas las tablas
```bash
# Tablas del schema source
docker exec sghu-postgres psql -U sghu_user -d sghu -c "\dt source.*"

# Tablas del schema sghu
docker exec sghu-postgres psql -U sghu_user -d sghu -c "\dt sghu.*"
```

#### Ver estructura de una tabla
```bash
docker exec sghu-postgres psql -U sghu_user -d sghu -c "\d+ source.programs"
docker exec sghu-postgres psql -U sghu_user -d sghu -c "\d+ source.students"
```

#### Ver datos de una tabla
```bash
# Primeros 5 programas
docker exec sghu-postgres psql -U sghu_user -d sghu -c "SELECT * FROM source.programs LIMIT 5;"

# Primeros 10 estudiantes
docker exec sghu-postgres psql -U sghu_user -d sghu -c "SELECT id, code, first_name, last_name, email, program_id FROM source.students LIMIT 10;"
```

### 3. Script Python

```bash
cd backend
python3 scripts/view_tables.py

# Ver estructura de una tabla específica
python3 scripts/view_tables.py --schema source --table students --structure

# Ver muestra de datos
python3 scripts/view_tables.py --schema source --table students --sample --limit 10
```

## 📋 Consultas Útiles para Presentación

### Ver Programas Académicos
```sql
SELECT id, code, name, faculty, duration_semesters, credits_required 
FROM source.programs 
ORDER BY id;
```

### Ver Asignaturas por Programa
```sql
SELECT 
    p.code as programa,
    p.name as programa_nombre,
    COUNT(s.id) as total_asignaturas,
    SUM(s.credits) as total_creditos
FROM source.programs p
LEFT JOIN source.subjects s ON s.program_id = p.id
GROUP BY p.id, p.code, p.name
ORDER BY p.id;
```

### Ver Estudiantes con su Programa
```sql
SELECT 
    s.id,
    s.code,
    s.first_name || ' ' || s.last_name as nombre_completo,
    s.email,
    p.code as programa,
    p.name as programa_nombre
FROM source.students s
JOIN source.programs p ON p.id = s.program_id
ORDER BY s.id
LIMIT 10;
```

### Ver Secciones Disponibles
```sql
SELECT 
    cs.id as seccion_id,
    s.code as asignatura_codigo,
    s.name as asignatura_nombre,
    cs.section_number,
    cs.capacity,
    cs.enrolled_count,
    (cs.capacity - cs.enrolled_count) as cupos_disponibles
FROM source.course_sections cs
JOIN source.subjects s ON s.id = cs.subject_id
WHERE cs.period_id = 1
ORDER BY s.code, cs.section_number
LIMIT 20;
```

### Ver Horarios de una Sección
```sql
SELECT 
    cs.id as seccion_id,
    s.code as asignatura,
    cs.section_number,
    CASE ss.day_of_week
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sábado'
    END as dia,
    ss.start_time,
    ss.end_time,
    ss.session_type
FROM source.course_sections cs
JOIN source.subjects s ON s.id = cs.subject_id
JOIN source.section_schedules ss ON ss.section_id = cs.id
WHERE cs.id = 1
ORDER BY ss.day_of_week, ss.start_time;
```

### Ver Horarios Generados
```sql
SELECT 
    gs.id as horario_id,
    s.code as estudiante,
    gs.generation_method,
    gs.quality_score,
    gs.processing_time,
    gs.status,
    gs.created_at
FROM sghu.generated_schedules gs
JOIN sghu.student_enrollments se ON se.id = gs.enrollment_id
JOIN source.students s ON s.id = se.student_id
ORDER BY gs.created_at DESC
LIMIT 10;
```

### Estadísticas Generales
```sql
SELECT 
    'Programas' as categoria,
    COUNT(*)::text as total
FROM source.programs
UNION ALL
SELECT 
    'Asignaturas' as categoria,
    COUNT(*)::text as total
FROM source.subjects
UNION ALL
SELECT 
    'Estudiantes' as categoria,
    COUNT(*)::text as total
FROM source.students
UNION ALL
SELECT 
    'Profesores' as categoria,
    COUNT(*)::text as total
FROM source.professors
UNION ALL
SELECT 
    'Aulas' as categoria,
    COUNT(*)::text as total
FROM source.classrooms
UNION ALL
SELECT 
    'Secciones (Período 1)' as categoria,
    COUNT(*)::text as total
FROM source.course_sections
WHERE period_id = 1;
```

## 🎯 Ejemplos para Demostración en Vivo

### 1. Mostrar estructura del sistema
```bash
# Ver todas las tablas
docker exec sghu-postgres psql -U sghu_user -d sghu -c "\dt source.*"
docker exec sghu-postgres psql -U sghu_user -d sghu -c "\dt sghu.*"
```

### 2. Mostrar datos de ejemplo
```bash
# Ver un estudiante completo
docker exec sghu-postgres psql -U sghu_user -d sghu -c "
SELECT 
    s.id, s.code, s.first_name || ' ' || s.last_name as nombre,
    p.code as programa, p.name as programa_nombre
FROM source.students s
JOIN source.programs p ON p.id = s.program_id
WHERE s.id = 1;
"

# Ver secciones de una asignatura
docker exec sghu-postgres psql -U sghu_user -d sghu -c "
SELECT cs.id, s.code, s.name, cs.section_number, cs.capacity, cs.enrolled_count
FROM source.course_sections cs
JOIN source.subjects s ON s.id = cs.subject_id
WHERE cs.subject_id = 1;
"
```

### 3. Mostrar horario generado
```bash
docker exec sghu-postgres psql -U sghu_user -d sghu -c "
SELECT 
    gs.id, s.code as estudiante, gs.generation_method, 
    gs.status, gs.processing_time
FROM sghu.generated_schedules gs
JOIN sghu.student_enrollments se ON se.id = gs.enrollment_id
JOIN source.students s ON s.id = se.student_id
ORDER BY gs.created_at DESC
LIMIT 5;
"
```

## 📝 Archivo SQL con Todas las Consultas

Puedes usar el archivo `backend/scripts/queries_presentacion.sql` que contiene todas estas consultas organizadas. Para ejecutarlo:

```bash
docker exec -i sghu-postgres psql -U sghu_user -d sghu < backend/scripts/queries_presentacion.sql
```

## 💡 Tips para la Presentación

1. **Prepara consultas específicas** antes de la presentación
2. **Usa el script automatizado** para mostrar estructura general
3. **Ten ejemplos de datos** listos para mostrar
4. **Muestra relaciones** entre tablas (foreign keys)
5. **Destaca los dos schemas**: `source` (datos externos) y `sghu` (datos del sistema)

## 🔗 Conexión Directa a PostgreSQL (Opcional)

Si prefieres usar un cliente gráfico:

```bash
# Host: localhost
# Port: 5433
# Database: sghu
# User: sghu_user
# Password: sghu_pass
```

Puedes usar herramientas como:
- pgAdmin
- DBeaver
- TablePlus
- DataGrip

